import sys
from interface import DressUpApp

def main():
    try:
        app = DressUpApp()
        
        print("Aplikace DressUp se spouští...")
        
        app.mainloop()
        
    except Exception as e:
        print(f"Došlo k chybě při spouštění aplikace: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()