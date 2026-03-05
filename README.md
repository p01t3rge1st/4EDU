# Geiger Monitor

Aplikacja do monitorowania promieniowania w czasie rzeczywistym dla systemu Linux, wyświetlająca dane z liczników Geigera podłączonych przez port szeregowy.

## Funkcje

- 📊 Wizualizacja CPM (Counts Per Minute) w czasie rzeczywistym
- 📈 Wykres CPS (Counts Per Second) z ostatnich 60 sekund
- 🎯 Logarytmiczny wskaźnik analogowy wyświetlający dawkę w µSv/h
- 🔄 Automatyczne wykrywanie portów szeregowych licznika Geigera
- ⚙️ Konfigurowalny współczynnik konwersji (µSv/h na CPS)
- 📝 Pełny dziennik próbek ze stemplami czasowymi
- 🐧 Natywna aplikacja Linux z PyQt6

## Wymagania

- Python 3.8 lub nowszy
- PyQt6 (6.0+)
- PySerial (3.5+)
- System Linux

## Instalacja

### Ze źródeł

```bash
git clone https://github.com/yourusername/geiger-monitor.git
cd geiger-monitor
pip install -e .
```

### Użycie Flatpaka

Zamień `yourusername` na właściwą nazwę:

```bash
flatpak install flathub org.example.GeigerMonitor
flatpak run org.example.GeigerMonitor
```

### Z PyPI (po opublikowaniu)

```bash
pip install geiger-monitor
```

## Użytkowanie

### Uruchomienie aplikacji

Jeśli zainstalowano przez pip:
```bash
geiger-monitor
```

Lub bezpośrednio ze źródeł:
```bash
python -m geiger_monitor.main
```

### Obsługa

1. Podłącz licznik Geigera kablem USB/szeregowym
2. Aplikacja automatycznie wykryje dostępne porty szeregowe
3. Kliknij **"Odśwież"** aby zaktualizować listę portów jeśli potrzebnie
4. Wybierz swój port z listy rozwijającej
5. Kliknij **"Połącz"** aby nawiązać połączenie
6. Aplikacja zacznie wyświetlać dane w czasie rzeczywistym

### Konfiguracja

- **Port**: Wybierz port szeregowy podłączonego licznika
- **Szybkość**: Domyślnie 9600 (zmień w kodzie jeśli potrzebnie)
- **Współczynnik konwersji**: Stosunek µSv/h na CPS (zależy od modelu licznika)

## Budowanie Flatpaka

### Wymagania wstępne

```bash
sudo apt install flatpak flatpak-builder
flatpak install flathub org.freedesktop.Platform//22.08 org.freedesktop.Sdk//22.08
flatpak install flathub org.freedesktop.Sdk.Extension.python3//22.08
```

### Budowanie

```bash
cd geiger-monitor
flatpak-builder build-dir flatpak/org.example.GeigerMonitor.yml --user --install-deps-from=flathub
```

### Uruchamianie

```bash
flatpak-builder --run build-dir flatpak/org.example.GeigerMonitor.yml geiger-monitor
```

### Tworzenie pakietu do dystrybucji

```bash
flatpak-builder build-dir flatpak/org.example.GeigerMonitor.yml
flatpak build-bundle build-dir geiger-monitor.flatpak org.example.GeigerMonitor
# Udostępnij plik geiger-monitor.flatpak
```

Inni mogą go zainstalować za pomocą:
```bash
flatpak install geiger-monitor.flatpak
```

## Architektura

```
geiger_monitor/
├── __init__.py           # Inicjalizacja pakietu
├── main.py               # Punkt wejścia aplikacji
├── main_window.py        # Główne okno UI i logika
└── analog_gauge.py       # Widget logarytmicznego wskaźnika
```

### Komponenty

- **MainWindow**: Obsługuje komunikację szeregową, przetwarzanie danych i aktualizacje UI
- **AnalogGauge**: Niestandardowy widget do logarytmicznego wyświetlania dawki
- **Sample**: Klasa danych reprezentująca jeden pomiar

## Protokół szeregowy

Aplikacja oczekuje danych z licznika Geigera w następującym formacie:
- Jedna liczba dziesiętna na linię
- Każda linia reprezentuje zliczenia w jedną sekundę
- Szybkość transmisji: 9600 (8N1)

Przykładowe dane:
```
5
7
3
12
8
```

## Obliczanie dawki

Dawka (w µSv/h) obliczana jest jako:

$$\text{Dose Rate} = \text{CPS} \times \text{Conversion Factor}$$

Gdzie:
- **CPS**: Zliczenia na sekundę (z ostatniej próbki)
- **Conversion Factor**: Współczynnik specyficzny dla urządzenia (µSv/h na CPS)

**Uwaga**: Współczynnik konwersji silnie zależy od modelu licznika i typu tuby. Zapoznaj się z dokumentacją lub certyfikatem kalibracji urządzenia.

## Rozwój

### Przygotowanie środowiska dev

```bash
# Utwórz wirtualne środowisko
python -m venv venv
source venv/bin/activate

# Zainstaluj pakiet z zależnościami dev
pip install -e ".[dev]"
```

### Uruchamianie testów

```bash
pytest
```

### Jakość kodu

```bash
black src/
flake8 src/
mypy src/
```

## Rozwiązywanie problemów

### Port szeregowy nie jest wykrywany
- Upewnij się, że licznik Geigera jest podłączony i włączony
- Sprawdź kabel USB
- Na Linuksie sprawdź, czy użytkownik ma dostęp do portów szeregowych:
  ```bash
  sudo usermod -aG dialout $USER
  # Wyloguj się i zaloguj ponownie
  ```
- Spróbuj `ls /dev/ttyUSB*` lub `ls /dev/ttyACM*` w terminalu

### Brak wyświetlanych danych
- Zweryfikuj, że licznik wysyła dane (sprawdź za pomocą `minicom` lub `screen`)
- Sprawdź szybkość transmisji (musi się zgadzać z ustawieniami urządzenia)
- Zweryfikuj format danych (jedna liczba na linię)

### Aplikacja pada przy starcie
- Upewnij się, że PyQt6 jest prawidłowo zainstalowany: `pip install --upgrade PyQt6`
- Sprawdź wersję Pythona: `python --version` (musi być 3.8+)

## Licencja

MIT License - patrz plik LICENSE

## Contributing

Wkład mile widziani! Proszę:
1. Forkuj repozytorium
2. Utwórz gałąź funkcji
3. Commituj zmiany
4. Push do gałęzi
5. Utwórz Pull Request

## Changelog

### Wersja 1.0.0 (2024-01-01)
- Początkowe wydanie
- Wersja Python/PyQt6 (konwersja z C++)
- Obsługa Flatpaka
- Monitorowanie i wizualizacja w czasie rzeczywistym

