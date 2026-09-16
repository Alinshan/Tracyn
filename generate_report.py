from datetime import datetime

LOG_FILE = "alerts.log"
REPORT_FILE = "security_report.txt"


def generate_report():
    try:
        with open(LOG_FILE, "r") as log:
            alerts = log.readlines()
    except FileNotFoundError:
        print("No alerts.log file found.")
        print("Run the real-time monitor and generate some alerts first.")
        return

    low = 0
    medium = 0
    high = 0

    for alert in alerts:
        if "[LOW]" in alert:
            low += 1
        elif "[MEDIUM]" in alert:
            medium += 1
        elif "[HIGH]" in alert:
            high += 1

    total = low + medium + high

    report = []
    report.append("=" * 60)
    report.append("             FILE INTEGRITY SECURITY REPORT")
    report.append("=" * 60)
    report.append("")
    report.append(f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    report.append("ALERT SUMMARY")
    report.append("-" * 60)
    report.append(f"LOW alerts    : {low}")
    report.append(f"MEDIUM alerts : {medium}")
    report.append(f"HIGH alerts   : {high}")
    report.append(f"TOTAL alerts  : {total}")
    report.append("")
    report.append("SECURITY EVENTS")
    report.append("-" * 60)

    if alerts:
        for alert in alerts:
            report.append(alert.strip())
    else:
        report.append("No security events recorded.")

    report.append("")
    report.append("=" * 60)

    with open(REPORT_FILE, "w") as output:
        output.write("\n".join(report))

    print(f"Security report created: {REPORT_FILE}")


if __name__ == "__main__":
    generate_report()
