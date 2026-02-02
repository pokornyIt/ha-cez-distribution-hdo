# ČEZ Distribuce HDO (Home Assistant)

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz/)
[![GitHub Release](https://img.shields.io/github/v/release/pokornyIt/ha-cez-distribution-hdo)](https://github.com/pokornyIt/ha-cez-distribution-hdo/releases)
[![License](https://img.shields.io/github/license/pokornyIt/ha-cez-distribution-hdo)](LICENSE)

> [!CAUTION]
> This project was terminated and replaced by an integration developed by the community: [ČEZ HDO](https://github.com/Cmajda/ha_cez_distribuce).
> We recommend switching to this new integration, which offers more options and active development.

Home Assistant custom integration for **ČEZ Distribuce HDO** tariff switching schedules (NT/VT).
The integration uses the Python library `cez-distribution-hdo` to fetch schedule data and expose it as entities.

🇨🇿 Czech documentation: **[README.cs.md](README.cs.md)**

---

## Features

For each configured **EAN + HDO signal** the integration creates a single device with these entities:

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

Where:

- `<signal>` is sanitized for entity naming (e.g. `A1B` → `a1b`)
- `<prefix>` is either:
  - `hdo` (default), producing `hdo_<signal>_*`
  - your custom prefix (optional), producing `<prefix>_<signal>_*`

---

## Data source

The same HDO switching schedule data is available on the official ČEZ Distribuce portal:

- https://dip.cezdistribuce.cz/irj/portal/anonymous/casy-spinani/

---

## Entities overview

| Entity ID suffix         | Platform        | Description                               | Notes                                                         |
| ------------------------ | --------------- | ----------------------------------------- | ------------------------------------------------------------- |
| `low_tariff`             | `binary_sensor` | `true` when **low tariff (NT)** is active | Static default icon (can be overridden in UI)                 |
| `actual_tariff`          | `sensor`        | Current tariff (`NT` / `VT`)              | String state                                                  |
| `actual_tariff_start`    | `sensor`        | Start of current tariff window            | Timestamp (UTC → shown in local time)                         |
| `actual_tariff_end`      | `sensor`        | End of current tariff window              | Timestamp                                                     |
| `next_low_tariff_start`  | `sensor`        | Start of next **low tariff (NT)** window  | Timestamp                                                     |
| `next_low_tariff_end`    | `sensor`        | End of next **low tariff (NT)** window    | Timestamp                                                     |
| `next_high_tariff_start` | `sensor`        | Start of next **high tariff (VT)** window | Timestamp                                                     |
| `next_high_tariff_end`   | `sensor`        | End of next **high tariff (VT)** window   | Timestamp                                                     |
| `next_switch`            | `sensor`        | Next tariff switch time                   | Timestamp                                                     |
| `remain_actual`          | `sensor`        | Remaining time until the next switch      | State is **seconds**, attributes include formatted `HH:MM:SS` |

> Example entity IDs (default prefix): `sensor.hdo_a1b_next_switch`, `binary_sensor.hdo_a1b_low_tariff`

---

## Installation

### Option A: HACS (recommended)

1. **Open your Home Assistant**.
2. Go to **HACS**.
3. Select **Integrations**.
4. Open the menu (top right) and choose **Custom repositories**.
5. Add this repository and select **Integration** as category:
   - `https://github.com/pokornyIt/ha-cez-distribution-hdo`
6. In HACS, search for **ČEZ Distribuce HDO** and click **Download**.
7. Restart Home Assistant.

### Option B: Manual installation

1. Download the latest release from:
   - https://github.com/pokornyIt/ha-cez-distribution-hdo/releases
2. Copy the folder `custom_components/cez_distribuce_hdo` into your Home Assistant config directory:
   - `<config>/custom_components/cez_distribuce_hdo`
3. Restart Home Assistant.

---

## Configuration

1. **Open your Home Assistant**.
2. Go to **Settings → Devices & services**.
3. Click **Add integration**.
4. Search for **ČEZ Distribuce HDO**.

You will be asked for:

- **EAN code** (18 digits)
- **Optional prefix** (used for device/entity naming)
- If multiple HDO signals are available for the EAN, you will be asked to select one

### Multiple signals for one EAN

This integration uses a **1:1 model**:

- **1 config entry = 1 signal**
- If you want to add another signal for the same EAN, add the integration again and select a different signal.

---

## About entity IDs and prefix changes

Home Assistant keeps `entity_id` stable.

- The integration proposes default entity IDs based on prefix + signal when entities are created.
- If you later change the prefix in integration options, **existing entity IDs will NOT be renamed automatically**.

To rename an entity ID manually:

**Settings → Devices & services → Entities → (select entity) → Entity ID**

---

## Data refresh behavior

- A signal snapshot is computed periodically (default: every 5 seconds).
- Source schedule data is refreshed less frequently (default: every 8 hours).

---

## Issues / Support

Please report issues here:

- https://github.com/pokornyIt/ha-cez-distribution-hdo/issues

Include:
- Home Assistant version
- integration version
- a relevant log excerpt from **Settings → System → Logs**
