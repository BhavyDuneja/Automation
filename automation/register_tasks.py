"""Register the two Windows scheduled tasks for the current user (Task Scheduler XML via schtasks).

  AnantaSutra-Daily      every day at --daily-at in this PC's local time (default 10:00), from tomorrow
                         -> run-daily.ps1 (uses the AI subscription)
  AnantaSutra-Publisher  every 30 minutes, all day -> run-publisher.ps1 (pure Python; post times are IST)

Both run hidden through run-hidden.vbs, only while you are logged in, and catch up after the PC was off.

    python automation/register_tasks.py [--daily-at 09:00]
    python automation/register_tasks.py --remove
"""
import argparse
import datetime as dt
import os
import subprocess
import tempfile
from pathlib import Path
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
TASKS = {
    "AnantaSutra-Daily": ("run-daily.ps1", "AnantaSutra marketing daily routine"),
    "AnantaSutra-Publisher": ("run-publisher.ps1", "AnantaSutra social publisher (IST schedule)"),
}

TEMPLATE = """<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo><Description>{description}</Description></RegistrationInfo>
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>{start}</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByDay><DaysInterval>1</DaysInterval></ScheduleByDay>{repetition}
    </CalendarTrigger>
  </Triggers>
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
    <ExecutionTimeLimit>PT1H</ExecutionTimeLimit>
    <Enabled>true</Enabled>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>wscript.exe</Command>
      <Arguments>"{vbs}" "{script}"</Arguments>
      <WorkingDirectory>{root}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
"""
EVERY_30_MIN = """
      <Repetition><Interval>PT30M</Interval><Duration>P1D</Duration><StopAtDurationEnd>false</StopAtDurationEnd></Repetition>"""


def schtasks(*args):
    result = subprocess.run(["schtasks", *args], capture_output=True, text=True)
    return result.returncode, (result.stdout + result.stderr).strip()


def register(name, script, description, start, repetition=""):
    xml = TEMPLATE.format(
        description=escape(description), start=start.isoformat(timespec="seconds"), repetition=repetition,
        user=escape(f"{os.environ['USERDOMAIN']}\\{os.environ['USERNAME']}"),
        vbs=escape(str(HERE / "run-hidden.vbs")), script=escape(str(HERE / script)), root=escape(str(ROOT)))
    with tempfile.NamedTemporaryFile("w", suffix=".xml", encoding="utf-16", delete=False) as f:
        f.write(xml)
    try:
        code, out = schtasks("/Create", "/TN", name, "/XML", f.name, "/F")
    finally:
        os.unlink(f.name)
    print(f"{name}: {'registered' if code == 0 else 'FAILED'} - {out}")
    return code == 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--daily-at", default="10:00", help="local PC time HH:MM")
    ap.add_argument("--remove", action="store_true")
    args = ap.parse_args()

    if args.remove:
        for name in TASKS:
            print(name, schtasks("/Delete", "/TN", name, "/F")[1])
        return

    hour, minute = map(int, args.daily_at.split(":"))
    today = dt.datetime.now().replace(second=0, microsecond=0)
    # First daily run is tomorrow, so registering late in the day doesn't fire a catch-up run right away.
    first_daily = (today + dt.timedelta(days=1)).replace(hour=hour, minute=minute)
    ok = register("AnantaSutra-Daily", *TASKS["AnantaSutra-Daily"], first_daily)
    ok &= register("AnantaSutra-Publisher", *TASKS["AnantaSutra-Publisher"],
                   today.replace(hour=0, minute=0), EVERY_30_MIN)
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
