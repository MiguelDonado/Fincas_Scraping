import contextlib
import pickle
import pprint


def imprimir_datos_bonito(datos, file):
    # Utiliza pprint para manejar estructuras anidadas de manera legible
    pp = pprint.PrettyPrinter(indent=4, width=80, stream=file)

    # Formatea los campos principales
    file.write("\n--- Información Principal ---\n")
    file.write(f"ID Electrónico: {datos.get('electronical_id', 'No disponible')}\n")
    file.write(f"Delegación: {datos.get('delegation', 'No disponible')}\n")
    file.write(f"Número de Lote: {datos.get('lote_number', 'No disponible')}\n")
    file.write(
        f"Referencia Catastral: {datos.get('referencia_catastral', 'No disponible')}\n"
    )
    file.write(f"Precio: {datos.get('price', 'No disponible')} €\n")
    file.write(f"Localización: {datos.get('localizacion', 'No disponible')}\n")
    file.write(f"Municipio: {datos.get('municipio', 'No disponible')}\n")
    file.write(f"Clase: {datos.get('clase', 'No disponible')}\n")
    file.write(f"Uso: {datos.get('uso', 'No disponible')}\n")
    file.write(f"Coordenadas: {datos.get('coordenadas', 'No disponible')}\n")
    file.write(f"Código Postal: {datos.get('codigo_postal', 'No disponible')}\n")
    file.write(f"Provincia: {datos.get('province', 'No disponible')}\n")

    # Imprime detalles de la población
    file.write("\n--- Población ---\n")
    file.write(f"Población actual: {datos.get('population_now', 'No disponible')}\n")
    file.write(
        f"Población anterior: {datos.get('population_before', 'No disponible')}\n"
    )

    # Imprime información de empresas
    file.write("\n--- Empresas ---\n")
    empresas = datos.get("empresas")
    if empresas is not None:
        file.write(f"{empresas}\n")
    else:
        file.write("No disponible\n")

    # Imprime detalles de empresas asociadas a fincas
    file.write("\n--- Empresas Fincas ---\n")
    empresas_fincas = datos.get("empresas_fincas", [])
    for empresa in empresas_fincas:
        file.write(f"CIF: {empresa.get('cif', 'No disponible')}\n")
        file.write("Datos:\n")
        pp.pprint(empresa.get("data", "No disponible"))

    # Imprime detalles de usos de suelo
    file.write("\n--- Usos del Suelo ---\n")
    pp.pprint(datos.get("usos_suelo", "No disponible"))

    # Imprime las rutas de archivos
    file.write("\n--- Rutas de Archivos ---\n")
    rutas = {
        "PDF de Subasta": datos.get("auction_pdf_path"),
        "Ortofoto": datos.get("path_ortofoto_land"),
        "KML": datos.get("path_kml_land"),
        "Google Maps": datos.get("path_googlemaps_land"),
    }
    for nombre, ruta in rutas.items():
        file.write(f"{nombre}: {ruta if ruta else 'No disponible'}\n")


###### LOADING TESTING DATA ######
# Load it later
with open("Testing/data.pkl", "rb") as pkl_file:
    loaded_data = pickle.load(pkl_file)

# Save print things to a file
with open("output.txt", "w") as file:
    imprimir_datos_bonito(loaded_data, file)
