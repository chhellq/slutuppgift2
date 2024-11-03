import psutil
import json
import time
import logging
from datetime import datetime
import os
import msvcrt

class SystemMonitor:
    def __init__(self):
        self.alarms = {'CPU': None, 'Memory': None, 'Disk': None}
        self.started = False
        self.log_filename = f"logs/monitoring_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        self.setup_logging()
        self.load_alarms()
        logging.info("Programmet startat och huvudmenyn visas.")

    def setup_logging(self):
        """Initialiserar loggning och skapar loggmappen om den inte finns."""
        if not os.path.exists('logs'):
            os.makedirs('logs')
        logging.basicConfig(
            filename=self.log_filename,
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        logging.info("Loggning startad.")

    def start_monitoring(self):
        """Startar övervakningen och loggar händelsen."""
        print("Övervakning startad...")
        self.started = True
        logging.info("Övervakning aktiverad.")

    def load_alarms(self):
        """Laddar konfigurerade alarm från JSON-fil och loggar händelsen."""
        try:
            with open('data/alarms.json', 'r') as f:
                self.alarms = json.load(f)
            logging.info("Tidigare konfigurerade alarm har laddats.")
        except FileNotFoundError:
            self.alarms = {'CPU': None, 'Memory': None, 'Disk': None}
            logging.warning("Ingen alarmkonfigurationsfil hittades; ett nytt alarmobjekt har skapats.")

    def save_alarms(self):
        """Sparar aktuella alarm till JSON-fil och loggar händelsen."""
        with open('data/alarms.json', 'w') as f:
            json.dump(self.alarms, f)
        logging.info("Alarmkonfigurationer sparade till fil.")

    def sanitize_numeric_input(self, prompt, min_value=None, max_value=None):
        """Sanerar numerisk inmatning och loggar felaktiga inmatningar."""
        while True:
            user_input = input(prompt)
            try:
                value = int(user_input)
                if min_value is not None and value < min_value:
                    print(f"Värdet måste vara större än eller lika med {min_value}.")
                    logging.warning(f"Felaktig inmatning: {value} under minimumgränsen {min_value}.")
                elif max_value is not None and value > max_value:
                    print(f"Värdet måste vara mindre än eller lika med {max_value}.")
                    logging.warning(f"Felaktig inmatning: {value} över maximumgränsen {max_value}.")
                else:
                    logging.info(f"Användaren matade in värde: {value}")
                    return value
            except ValueError:
                print("Ogiltig inmatning, försök igen.")
                logging.error("Ogiltig inmatning: Användaren angav inte ett heltal.")

    def configure_alarm(self):
        """Konfigurerar alarm och loggar alla ändringar."""
        print("1. CPU-användning\n2. Minnesanvändning\n3. Diskanvändning\n4. Tillbaka till huvudmenyn")
        choice = self.sanitize_numeric_input("Välj ett alternativ (1-4): ", 1, 4)
        if choice in [1, 2, 3]:
            alarm_type = ['CPU', 'Memory', 'Disk'][choice - 1]
            threshold = self.sanitize_numeric_input(f"Ange tröskelvärde för {alarm_type}-användning (1-100%): ", 1, 100)
            self.alarms[alarm_type] = threshold
            print(f"Alarm för {alarm_type} inställt på {threshold}%")
            logging.info(f"Alarm konfigurerat: {alarm_type} vid {threshold}%")
            self.save_alarms()
        elif choice == 4:
            logging.info("Användaren återvände till huvudmenyn utan att konfigurera alarm.")

    def get_values(self):
        """Hämtar systemvärden och skickar tillbaka dom."""
        return psutil.cpu_percent(interval=1), psutil.virtual_memory().percent, psutil.disk_usage('/').percent

 
    def list_alarms(self):
        """Listar alla konfigurerade alarm i sorterad ordning och loggar visningshändelsen."""
        print("Konfigurerade alarm (sorterade):")
        # Lambdafunktion för att sortera alarmen vid utskrift
        sorted_alarms = sorted(
            ((alarm_type, threshold) for alarm_type, threshold in self.alarms.items() if threshold is not None),
            key=lambda item: item[1]
        )
        # Visa sorterade alarm
        for alarm_type, threshold in sorted_alarms:
            print(f"{alarm_type}: {threshold}%")
        input("Tryck Enter för att fortsätta...")
        logging.info("Användaren visade sorterade konfigurerade alarm.")
    def delete_alarm(self):
        """Tar bort ett specifikt alarm och loggar borttagningen."""
        alarms_with_thresholds = [(atype, thresh) for atype, thresh in self.alarms.items() if thresh is not None]
        if not alarms_with_thresholds:
            print("Inga alarm att ta bort.")
            logging.info("Inga alarm fanns att ta bort.")
            return

        print("Välj ett alarm att ta bort:")
        for i, (alarm_type, threshold) in enumerate(alarms_with_thresholds, start=1):
            print(f"{i}. {alarm_type}: {threshold}%")

        choice = self.sanitize_numeric_input("Välj numret på det alarm du vill ta bort: ", 1, len(alarms_with_thresholds))
        alarm_type = alarms_with_thresholds[choice - 1][0]
        removed_alarm = self.alarms[alarm_type]
        self.alarms[alarm_type] = None
        logging.info(f"Alarm för {alarm_type} vid {removed_alarm}% borttaget.")
        self.save_alarms()
        print(f"Alarm för {alarm_type} vid {removed_alarm}% borttaget")

    def check_alarms(self, cpu_usage, memory_usage, disk_usage):
        """Kontrollerar om några alarm har aktiverats och loggar varningar."""
        if self.alarms['CPU'] and cpu_usage > self.alarms['CPU']:
            print(f"***VARNING: CPU-användning över {self.alarms['CPU']}%***")
            logging.warning(f"CPU-användning överstiger {self.alarms['CPU']}%")
        if self.alarms['Memory'] and memory_usage > self.alarms['Memory']:
            print(f"***VARNING: Minnesanvändning över {self.alarms['Memory']}%***")
            logging.warning(f"Minnesanvändning överstiger {self.alarms['Memory']}%")
        if self.alarms['Disk'] and disk_usage > self.alarms['Disk']:
            print(f"***VARNING: Diskanvändning över {self.alarms['Disk']}%***")
            logging.warning(f"Diskanvändning överstiger {self.alarms['Disk']}%")

    def surveillance_mode(self):
        """Startar övervakningsläge som loopar tills en tangent trycks."""
        if not self.started:
            print("Övervakningen har inte startat.")
            logging.info("Övervakningsläge försökte startas utan att övervakningen var aktiverad.")
            return
        logging.info("Övervakningsläge startat.")
        while True:
            print("Övervakningsläge aktivt. Tryck på en knapp för att avsluta.")
            time.sleep(2)
            cpu_usage, memory_usage, disk_usage = self.get_values()
            self.check_alarms(cpu_usage, memory_usage, disk_usage)
            if msvcrt.kbhit():
                msvcrt.getch()
                logging.info("Övervakningsläge avbrutet av användaren.")
                break

    def main_menu(self):
        """Huvudmeny för användarinteraktion."""
        while True:
            print("\n--- Systemövervakningsmeny ---")
            print("1. Starta övervakning")
            print("2. Lista aktiva övervakningar")
            print("3. Konfigurera alarm")
            print("4. Lista konfigurerade alarm")
            print("5. Starta övervakningsläge")
            print("6. Ta bort alarm")
            print("7. Avsluta")

            choice = self.sanitize_numeric_input("Välj ett alternativ (1-7): ", 1, 7)

            if choice == 1:
                logging.info("Användaren valde att starta övervakning.")
                self.start_monitoring()
            elif choice == 2:
                logging.info("Användaren valde att lista aktiva övervakningar.")
                self.list_active_monitoring()
            elif choice == 3:
                logging.info("Användaren valde att konfigurera alarm.")
                self.configure_alarm()
            elif choice == 4:
                logging.info("Användaren valde att visa konfigurerade alarm.")
                self.list_alarms()
            elif choice == 5:
                logging.info("Användaren valde att starta övervakningsläge.")
                self.surveillance_mode()
            elif choice == 6:
                logging.info("Användaren valde att ta bort ett alarm.")
                self.delete_alarm()
            elif choice == 7:
                logging.info("Programmet avslutas av användaren.")
                print("Avslutar...")
                break


if __name__ == "__main__":
    monitor = SystemMonitor()
    monitor.main_menu()
