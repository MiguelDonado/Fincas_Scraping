# SUMMARY
The purpose of this file is to clear up the contents of the directories of this project.
## 1) .vscode/
It stores workspace settings. This makes it easy to share settings with other in Git i.e.

### 1.1) launch.json: Defines debugging configurations
`"program": "${workspaceFolder}/scrapingFincasHacienda/main.py"`: Specifies the entry point of the Python program to debug.

`${workspaceFolder}`: Placeholder for the root folder of the workspace

`"cwd": "${workspaceFolder}/scrapingFincasHacienda"`: Sets the cwd for the debugger. This ensures relative paths works fine.

## 2) data/
It stores downloaded files of scraped lands.

### 2.1) auction/
#### 2.1.1) <pliego.pdf>
### 2.2) catastro/
#### 2.2.1) <.kml>
#### 2.2.2) <.png>
(Catastro ortofoto)
### 2.3) googlemaps/
#### 2.3.1) <.png>
(one direction)
#### 2.3.2) <.png>
(two directions)
### 2.4) iberpix/
#### 2.4.1) <.png>
(curvas nivel)
#### 2.4.2) <.png>
(lidar)
#### 2.4.3) <.png>
(usos suelo)
#### 2.4.4) <.png>
(hidrografia)
### 2.5) report/
#### 2.5.1) <.pdf>
(Report valor catastral)

## 3) docs/
It stores theoretical info about some documents, terms...
### 3.1) catastro_price_report/
Files that explain terms used in catastro report document.
...

## 4) scrapingFincasHacienda/
It stores all the scripts.
To get the following representation I used `tree | grep -Ev '__pycache__|\.pyc$` (excluding pycache and pyc files).
```sh
├── Catastro 
│   ├── catastro.py
│   ├── constants.py
│   ├── __init__.py
│   └── report.py
├── Correos
│   ├── constants.py
│   ├── correos.py
│   └──  __init__.py
├── Database
│   ├── constants.py
│   ├── helpers.py
│   ├── __init__.py
│   ├── models
│   │   ├── agrupacion_cultivo.py
│   │   ├── aprovechamiento.py
│   │   ├── auction.py
│   │   ├── base_database.py
│   │   ├── clase.py
│   │   ├── codigo_postal.py
│   │   ├── cubierta_terrestre_codigee.py
│   │   ├── cubierta_terrestre_iberpix.py
│   │   ├── delegation.py
│   │   ├── empresa_finca.py
│   │   ├── empresa.py
│   │   ├── finca.py
│   │   ├── __init__.py
│   │   ├── locality.py
│   │   ├── lote.py
│   │   ├── municipio.py
│   │   ├── province.py
│   │   ├── territorio.py
│   │   ├── test2.py
│   │   ├── test.py
│   │   ├── uso.py
│   │   └── usos_suelo_hilucs.py
├── FincasProject.db
├── GoogleMaps
│   ├── constants.py
│   ├── GoogleMaps.py
│   ├── __init__.py
├── Hacienda
│   ├── auction_delegation.py
│   ├── constants.py
│   ├── data_pdf.py
│   ├── __init__.py
│   ├── pliego_url.py
├── Iberpix
│   ├── constants.py
│   ├── iberpix.py
│   ├── __init__.py
├── INE
│   ├── constants.py
│   ├── ine_num_transmisiones_fincas_rusticas.py
│   ├── ine_population.py
│   ├── __init__.py
├── logger_config.py
├── logs
│   ├── debug_250114.log
│   └── error_250114.log
├── main.py
├── Sabi
│   ├── constants.py
│   ├── __init__.py
│   └── sabi.py
└── utils.py
```

## 5) venv/

## 6) ScrapingFincasHacienda.code-workspace
File that contains settings about my workspace.

## 7) /scrapingFincasHacienda/Testing/
Directory that contains testing data to check that the 'insert_land_data', and so, the 'Database' package works fine.

