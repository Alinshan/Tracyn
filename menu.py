import subprocess


def show_menu():
    while True:
        print("\n" + "=" * 40)
        print("      FILE INTEGRITY MONITOR")
        print("=" * 40)
        print("1. Create baseline")
        print("2. Scan files")
        print("3. Start real-time monitoring")
        print("4. Generate security report")
        print("5. Exit")
        print("=" * 40)

        try:
            choice = input("Enter your choice: ")

            if choice == "1":
                subprocess.run(["python3", "fim.py", "--baseline"])

            elif choice == "2":
                subprocess.run(["python3", "fim.py", "--scan"])

            elif choice == "3":
                try:
                    subprocess.run(["python3", "realtime_monitor.py"])
                except KeyboardInterrupt:
                    print("\nReal-time monitoring stopped.")

            elif choice == "4":
                subprocess.run(["python3", "generate_report.py"])

            elif choice == "5":
                print("Exiting File Integrity Monitor.")
                break

            else:
                print("Invalid choice. Please select 1-5.")

        except KeyboardInterrupt:
            print("\nExiting File Integrity Monitor.")
            break


if __name__ == "__main__":
    show_menu()
