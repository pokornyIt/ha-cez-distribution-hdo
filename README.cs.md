# ČEZ Distribuce HDO (Home Assistant)

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz/)
[![GitHub Release](https://img.shields.io/github/v/release/pokornyIt/ha-cez-distribution-hdo)](https://github.com/pokornyIt/ha-cez-distribution-hdo/releases)
[![License](https://img.shields.io/github/license/pokornyIt/ha-cez-distribution-hdo)](LICENSE)

Vlastní integrace pro Home Assistant pro **ČEZ Distribuce HDO** (přepínání tarifu NT/VT).
Integrace používá Python knihovnu `cez-distribution-hdo`, která načte rozpis spínání a spočítá aktuální stav i následující okna.

---

## Funkce

Pro každý nakonfigurovaný **EAN + HDO signál** vytvoří integrace jedno zařízení s entitami:

- `binary_sensor.<prefix>_<signal>_low_tariff`
- `sensor.<prefix>_<signal>_actual_tariff`
- `sensor.<prefix>_<signal>_actual_tariff_start`
- `sensor.<prefix>_<signal>_actual_tariff_end`
- `sensor.<prefix>_<signal>_next_low_tariff_start`
- `sensor.<prefix>_<signal>_next_low_tariff_end`
- `sensor.<prefix>_<signal>_next_high_tariff_start`
- `sensor.<prefix>_<signal>_next_high_tariff_end`
- `sensor.<prefix>_<signal>_next_switch`
- `sensor.<prefix>_<signal>_remain_actual`

Kde:

- `<signal>` je upravený pro entity naming (např. `A1B` → `a1b`)
- `<prefix>` je buď:
  - `hdo` (výchozí), tedy `hdo_<signal>_*`
  - nebo tvůj vlastní prefix (volitelné), tedy `<prefix>_<signal>_*`

---

## Zdroj dat

Stejná data o časech spínání HDO jsou dostupná také na oficiálním portálu ČEZ Distribuce:

- https://dip.cezdistribuce.cz/irj/portal/anonymous/casy-spinani/

---

## Přehled entit

| Suffix entity ID         | Platforma       | Popis                                         | Poznámka                                               |
| ------------------------ | --------------- | --------------------------------------------- | ------------------------------------------------------ |
| `low_tariff`             | `binary_sensor` | `true`, pokud je aktivní **nízký tarif (NT)** | Statická výchozí ikona (lze přepsat v UI)              |
| `actual_tariff`          | `sensor`        | Aktuální tarif (`NT` / `VT`)                  | Textový stav                                           |
| `actual_tariff_start`    | `sensor`        | Začátek aktuálního okna tarifu                | Timestamp (UTC → zobrazeno v lokálním čase)            |
| `actual_tariff_end`      | `sensor`        | Konec aktuálního okna tarifu                  | Timestamp                                              |
| `next_low_tariff_start`  | `sensor`        | Začátek příštího okna **NT**                  | Timestamp                                              |
| `next_low_tariff_end`    | `sensor`        | Konec příštího okna **NT**                    | Timestamp                                              |
| `next_high_tariff_start` | `sensor`        | Začátek příštího okna **VT**                  | Timestamp                                              |
| `next_high_tariff_end`   | `sensor`        | Konec příštího okna **VT**                    | Timestamp                                              |
| `next_switch`            | `sensor`        | Čas příštího přepnutí tarifu                  | Timestamp                                              |
| `remain_actual`          | `sensor`        | Zbývající čas do příštího přepnutí            | Stav je **v sekundách**, atribut obsahuje i `HH:MM:SS` |

> Příklad entity ID (výchozí prefix): `sensor.hdo_a1b_next_switch`, `binary_sensor.hdo_a1b_low_tariff`

---

## Instalace

### Varianta A: HACS (doporučeno)

1. **Otevři Home Assistant**.
2. Jdi do **HACS**.
3. Vyber **Integrations**.
4. Otevři menu (vpravo nahoře) → **Custom repositories**.
5. Přidej repozitář a vyber kategorii **Integration**:
   - `https://github.com/pokornyIt/ha-cez-distribution-hdo`
6. V HACS najdi **ČEZ Distribuce HDO** a klikni na **Download**.
7. Restartuj Home Assistant.

### Varianta B: Ruční instalace

1. Stáhni poslední release z:
   - https://github.com/pokornyIt/ha-cez-distribution-hdo/releases
2. Zkopíruj složku `custom_components/cez_distribuce_hdo` do konfigurace Home Assistant:
   - `<config>/custom_components/cez_distribuce_hdo`
3. Restartuj Home Assistant.

---

## Konfigurace

1. **Otevři Home Assistant**.
2. Jdi do **Nastavení → Zařízení a služby**.
3. Klikni na **Přidat integraci**.
4. Vyhledej **ČEZ Distribuce HDO**.

Zadáš:
- **EAN kód** (18 číslic)
- **Volitelný prefix** (pro pojmenování zařízení/entit)
- Pokud je pro EAN dostupných více signálů, vybereš konkrétní signál

### Více signálů pro jeden EAN

Integrace funguje v režimu **1:1**:

- 1 konfigurace = 1 signál
- Pro další signál přidej integraci znovu a vyber jiný signál.

---

## Entity ID a změna prefixu

Home Assistant drží `entity_id` stabilní.

- Integrace při vytvoření navrhne výchozí entity ID podle prefixu + signálu.
- Pokud později změníš prefix v nastavení integrace, **stávající entity ID se automaticky nepřejmenují**.

Přejmenování jde ručně v UI:

**Nastavení → Zařízení a služby → Entity → (vyber entitu) → Entity ID**

---

## Aktualizace dat

- Snapshot signálu se počítá pravidelně (default: každých 5 sekund).
- Načtení/obnova zdrojových dat probíhá méně často (default: každých 8 hodin).

---

## Issues / Podpora

Chyby hlásit zde:

- https://github.com/pokornyIt/ha-cez-distribution-hdo/issues

Uveď:
- verzi Home Assistant
- verzi integrace
- relevantní část logu z **Nastavení → Systém → Protokoly**
