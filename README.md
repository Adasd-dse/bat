# Aplicatie analiza profit printare 3D

Acest proiect ofera o aplicatie de tip CLI (linie de comanda) in Python pentru a analiza performanta financiara a unei companii de printare 3D si a genera prognoze scurte care ajuta la maximizarea profitului.

## Functionalitati
- Incarca date financiare din CSV (luna, venituri, costuri variabile, costuri fixe, volum de printare).
- Calculeaza profitul, marja si tendinta lunara.
- Genereaza prognoza de profit pentru urmatoarele luni folosind regresie liniara simpla.
- Ruleaza scenarii de ajustare a pretului si a costurilor variabile pentru a vedea impactul asupra profitului si punctul de break-even.
- Poate exporta rezultatele in format JSON pentru raportare.

## Structura fisierului CSV
Fisierul trebuie sa contina headerul:

```
month,revenue,variable_costs,fixed_costs,print_volume
```

Un exemplu se gaseste in `data/sample_financials.csv`.

## Utilizare
1. Asigura-te ca ai Python 3.10+ instalat.
2. Ruleaza comanda:

```bash
python app.py data/sample_financials.csv --forecast-months 3 --price-adjust 0.05 --variable-cost-adjust -0.02 --output-json rapoarte/rezultat.json
```

Argumente importante:
- `file` – calea catre CSV.
- `--forecast-months` – cate luni sa fie prognozate (default: 3).
- `--price-adjust` – ajustare procentuala a veniturilor (ex: `0.05` pentru +5%).
- `--variable-cost-adjust` – ajustare procentuala a costurilor variabile (ex: `-0.02` pentru reducere de 2%).
- `--output-json` – calea catre fisierul JSON unde se salveaza raportul.

## Extindere
- Integrare cu baze de date pentru import automat de date.
- Inlocuirea regresiei liniare cu modele mai avansate (ex. ARIMA/Prophet).
- Vizualizari grafice ale trendurilor si scenariilor.
