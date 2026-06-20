# 🌧️ Uttar Pradesh Rainfall & Weather EDA (2005–2025)

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-Latest-red?style=flat-square&logo=streamlit)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

> End-to-end Exploratory Data Analysis on 565,210 daily weather records across 73 UP districts (2005–2025) using NASA POWER climate data — with a fully interactive Streamlit dashboard.

---

## 📊 Dataset Overview

| Feature | Detail |
|---------|--------|
| Records | 565,210 daily weather records |
| Period | 2005–2025 (21 years) |
| Districts | 73 Uttar Pradesh districts |
| Source | NASA POWER Climate Data |
| Key Variable | PRECTOTCORR (Daily Rainfall mm) |
| Features | 20 columns (rainfall, temperature, humidity, wind, UV) |

---

## 🚀 Quick Start

```bash
git clone https://github.com/<your-username>/up-rainfall-eda.git
cd up-rainfall-eda
pip install -r requirements.txt
streamlit run app.py
```

---

## 📁 Project Structure

```
up-rainfall-eda/
│
├── UP_rainfall_dataset.csv      # Dataset (NASA POWER)
├── UP_Rainfall_EDA.ipynb        # Full EDA Jupyter Notebook
├── app.py                       # Streamlit Dashboard
├── requirements.txt
└── README.md
```

---

## 🔍 Key Analyses

- **Rainfall Overview** — Distribution, intensity categories, rain vs dry days
- **Annual Trends** — 21-year rainfall & temperature trends
- **Seasonal & Monthly** — Monsoon, Pre-Monsoon, Winter patterns
- **District Analysis** — Rainiest & driest districts across UP
- **Temperature** — Max/Min trends, monthly range, temp vs rainfall
- **Humidity & Wind** — Seasonal humidity, UV index, wind speed
- **Extreme Events** — Heavy rainfall events (>64.5mm) by year, month, district

---

## 🌧️ Key Insights

- Monsoon season contributes **~80%** of annual rainfall
- **Eastern UP districts** receive significantly more rainfall than western ones
- **July & August** are the peak monsoon months
- Extreme rainfall events (>64.5mm) are concentrated in **monsoon months**
- Clear **rising temperature trend** visible over 2005–2025

---

## 🛠️ Tech Stack

`Python` · `Pandas` · `NumPy` · `Matplotlib` · `Seaborn` · `Plotly` · `Streamlit`

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
