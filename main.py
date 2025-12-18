# main.py

from cli_view import CLI

def main():
    cli = CLI()

    # LOGIN SCREEN
    if not cli.loginMenu():
        print("Goodbye!")
        return

    # DASHBOARD
    cli.dashboard()

if __name__ == "__main__":
    main()
