"""Register the Windows scheduled tasks for the current user (Task Scheduler XML via schtasks).

  AnantaSutra-Daily      every day at --daily-at in this PC's local time (default 10:00), from tomorrow
                         -> run-daily.ps1 (uses the AI subscription)
  AnantaSutra-Publisher  every 30 minutes, all day -> run-publisher.ps1 (pure Python; post times are IST)
  AnantaSutra-Dashboard  at logon -> scripts/dashboard.py on http://localhost:8765 (pure Python)

All run hidden, only while you are logged in; the first two catch up after the PC was off.

    python automation/register_tasks.py [--daily-at 09:00]
    python automation/register_tasks.py --remove
"""
import argparse
import datetime as dt
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
USER = f"{os.environ['USERDOMAIN']}\\{os.environ['USERNAME']}"
NAMES = ["AnantaSutra-Daily", "AnantaSutra-Publisher", "AnantaSutra-Dashboard"]

TEMPLATE = """<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo><Description>{description}</Description></RegistrationInfo>
  <Triggers>{trigger}</Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>{user}</UserId>
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <StartWhenAvailable>true</StartWhenAvailable>
    <ExecutionTimeLimit>{time_limit}</ExecutionTimeLimit>
    <Enabled>true</Enabled>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>{command}</Command>
      <Arguments>{arguments}</Arguments>
      <WorkingDirectory>{root}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
"""
DAILY = """
    <CalendarTrigger>
      <StartBoundary>{start}</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByDay><DaysInterval>1</DaysInterval></ScheduleByDay>{repetition}
    </CalendarTrigger>"""
EVERY_30_MIN = """
      <Repetition><Interval>PT30M</Interval><Duration>P1D</Duration><StopAtDurationEnd>false</StopAtDurationEnd></Repetition>"""
AT_LOGON = """
    <LogonTrigger><Enabled>true</Enabled><UserId>{user}</UserId></LogonTrigger>"""


def schtasks(*args):
    result = subprocess.run(["schtasks", *args], capture_output=True, text=True)
    return result.returncode, (result.stdout + result.stderr).strip()


def register(name, description, trigger, command, arguments, time_limit="PT1H"):
    xml = TEMPLATE.format(description=escape(description), trigger=trigger, user=escape(USER), time_limit=time_limit,
                          command=escape(command), arguments=escape(arguments), root=escape(str(ROOT)))
    with tempfile.NamedTemporaryFile("w", suffix=".xml", encoding="utf-16", delete=False) as f:
        f.write(xml)
    try:
        code, out = schtasks("/Create", "/TN", name, "/XML", f.name, "/F")
    finally:
        os.unlink(f.name)
    print(f"{name}: {'registered' if code == 0 else 'FAILED'} - {out}")
    return code == 0


def hidden_ps1(script):
    return "wscript.exe", f'"{HERE / "run-hidden.vbs"}" "{HERE / script}"'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--daily-at", default="10:00", help="local PC time HH:MM")
    ap.add_argument("--remove", action="store_true")
    args = ap.parse_args()

    if args.remove:
        for name in NAMES:
            print(name, schtasks("/Delete", "/TN", name, "/F")[1])
        return

    hour, minute = map(int, args.daily_at.split(":"))
    now = dt.datetime.now().replace(second=0, microsecond=0)
    # First daily run is tomorrow, so registering late in the day doesn't fire a catch-up run right away.
    first_daily = (now + dt.timedelta(days=1)).replace(hour=hour, minute=minute)
    midnight = now.replace(hour=0, minute=0)
    pythonw = Path(sys.executable).with_name("pythonw.exe")

    ok = register("AnantaSutra-Daily", "AnantaSutra marketing daily routine",
                  DAILY.format(start=first_daily.isoformat(), repetition=""), *hidden_ps1("run-daily.ps1"))
    ok &= register("AnantaSutra-Publisher", "AnantaSutra social publisher (IST schedule)",
                   DAILY.format(start=midnight.isoformat(), repetition=EVERY_30_MIN), *hidden_ps1("run-publisher.ps1"))
    ok &= register("AnantaSutra-Dashboard", "AnantaSutra dashboard on http://localhost:8765",
                   AT_LOGON.format(user=escape(USER)), str(pythonw), f'"{ROOT / "scripts" / "dashboard.py"}"',
                   time_limit="PT0S")  # PT0S = no time limit: the dashboard keeps running
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
