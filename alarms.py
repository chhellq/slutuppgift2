import json
import logging
from utils import sanitize_numeric_input
#klass för att hantera alarm    
class AlarmManager:
    def __init__(self):
        self.alarms = {
            'CPU': None,
            'Memory': None,
            'Disk': None
        }
        self.load_alarms()

    def configure_alarm(self):
        print("1. CPU-användning\n2. Minnesanvändning\n3. Diskanvändning\n4. Tillbaka till huvudmenyn")
        choice = sanitize_numeric_input("Välj ett alternativ (1-4): ", 1, 4)

        if choice in [1, 2, 3]:
            alarm_type = ['CPU', 'Memory', 'Disk'][choice - 1]
            threshold = sanitize_numeric_input(f"Ange tröskelvärde för {alarm_type}-användning (1-100%): ", 1, 100)
            self.alarms[alarm_type] = threshold
            print(f"Alarm för {alarm_type} inställt på {threshold}%")
            logging.info(f"Alarm konfigurerat för {alarm_type} vid {threshold}%")
            self.save_alarms()
        elif choice == 4:
            return
#funktion för att lista alarm om det finns, annars skrivs "Inga alarm konfigurerade"
    def list_alarms(self):
        print("Konfigurerade alarm:")
        for alarm_type, threshold in self.alarms.items():
            if threshold is not None:
                print(f"{alarm_type}: {threshold}%")
            else:
                print(f"{alarm_type}: Inga alarm konfigurerade")
        input("Tryck Enter för att fortsätta...")
#function för att ta bort alarm om det finns, annars skrivs "Inga alarm att ta bort."
    def delete_alarm(self):
        alarms_with_thresholds = [(atype, thresh) for atype, thresh in self.alarms.items() if thresh is not None]
        
        if not alarms_with_thresholds:
            print("Inga alarm att ta bort.")
            return

        print("Välj ett alarm att ta bort:")
        for i, (alarm_type, threshold) in enumerate(alarms_with_thresholds, start=1):
            print(f"{i}. {alarm_type}: {threshold}%")

        choice = sanitize_numeric_input("Välj numret på det alarm du vill ta bort: ", 1, len(alarms_with_thresholds))
        alarm_type = alarms_with_thresholds[choice - 1][0]
        removed_alarm = self.alarms[alarm_type]
        self.alarms[alarm_type] = None
        logging.info(f"Alarm för {alarm_type} vid {removed_alarm}% borttaget")
        self.save_alarms()
        print(f"Alarm för {alarm_type} vid {removed_alarm}% borttaget")
  #funktion för att hämta värden från systemet
    def check_alarms(self, cpu_usage, memory_usage, disk_usage):
        if self.alarms['CPU'] and cpu_usage > self.alarms['CPU']:
            print(f"CPU-användning är över {self.alarms['CPU']}%!")
            logging.warning(f"CPU-användning överstiger {self.alarms['CPU']}%")
        if self.alarms['Memory'] and memory_usage > self.alarms['Memory']:
            print(f"Minnesanvändning är över {self.alarms['Memory']}%!")
            logging.warning(f"Minnesanvändning överstiger {self.alarms['Memory']}%")
        if self.alarms['Disk'] and disk_usage > self.alarms['Disk']:
            print(f"Diskanvändning är över {self.alarms['Disk']}%!")
            logging.warning(f"Diskanvändning överstiger {self.alarms['Disk']}%")
#funktion för att spara alarm
    def save_alarms(self):
        with open('data/alarms.json', 'w') as f:
           json.dump(self.alarms, f)
#funktion för att ladda alarm från fil
    def load_alarms(self):
        try:
            with open('data/alarms.json', 'r') as f:
                self.alarms = json.load(f)
        except FileNotFoundError:
            self.alarms = {'CPU': None, 'Memory': None, 'Disk': None}
