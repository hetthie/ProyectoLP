"""
============================================================
 SCRIPT PRINCIPAL - Analizador Lexico y Sintactico C++
============================================================
Al ejecutar sin argumentos, abre:
  1. Explorador de archivos para seleccionar el .cpp
  2. Cuadro para ingresar el nombre del estudiante

Siempre ejecuta AMBOS analisis (lexico y sintactico)
y genera los 2 logs automaticamente.

USO:
    python main.py                             -> abre ventana grafica
    python main.py algoritmo1.cpp AndieBarreno -> directo por terminal
============================================================
"""

import sys
import os
import datetime
from lexer import lexer, errores_lexicos
from parser import parser, errores_sintacticos


def analizar_lexico(codigo):
    errores_lexicos.clear()
    lexer.lineno = 1
    lexer.input(codigo)
    resultados = []
    while True:
        tok = lexer.token()
        if not tok:
            break
        resultados.append((tok.type, tok.value, tok.lineno))
    return resultados, list(errores_lexicos)


def analizar_sintactico(codigo):
    errores_sintacticos.clear()
    lexer.lineno = 1
    resultado = parser.parse(codigo, lexer=lexer)
    return resultado, list(errores_sintacticos)


def generar_log(fase, nombre_apellido, codigo_fuente, resultados, errores, carpeta="."):
    ahora = datetime.datetime.now()
    fecha_hora = ahora.strftime("%d-%m-%Y-%Hh%M")
    nombre_archivo = f"{fase}-{nombre_apellido}-{fecha_hora}.txt"
    ruta = os.path.join(carpeta, nombre_archivo)

    with open(ruta, "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write(f"ANALIZADOR {fase.upper()} - C++\n")
        f.write(f"Estudiante: {nombre_apellido}\n")
        f.write(f"Fecha y hora: {ahora.strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write("=" * 60 + "\n\n")

        f.write("CODIGO FUENTE ANALIZADO:\n")
        f.write("-" * 60 + "\n")
        f.write(codigo_fuente.rstrip() + "\n")
        f.write("-" * 60 + "\n\n")

        if fase == "lexico":
            f.write(f"TOKENS RECONOCIDOS ({len(resultados)}):\n")
            f.write("-" * 60 + "\n")
            f.write(f"{'LINEA':<8}{'TOKEN':<20}{'VALOR'}\n")
            f.write("-" * 60 + "\n")
            for tipo, valor, linea in resultados:
                f.write(f"{linea:<8}{tipo:<20}{valor}\n")
        else:
            f.write("RESULTADO DEL ANALISIS SINTACTICO:\n")
            f.write("-" * 60 + "\n")
            if not errores:
                f.write("El programa es sintacticamente VALIDO.\n")
            else:
                f.write("Se encontraron errores sintacticos:\n")

        f.write(f"\nERRORES ({len(errores)}):\n")
        f.write("-" * 60 + "\n")
        if errores:
            for err in errores:
                f.write(err + "\n")
        else:
            f.write("Ningun error detectado.\n")

    return ruta


def pedir_datos_con_ventana():
    import tkinter as tk
    from tkinter import filedialog, simpledialog

    root = tk.Tk()
    root.withdraw()

    origen = filedialog.askopenfilename(
        title="Selecciona tu archivo C++",
        filetypes=[("Archivos C++", "*.cpp"), ("Todos los archivos", "*.*")]
    )
    if not origen:
        print("Operacion cancelada.")
        sys.exit(0)

    nombre_apellido = simpledialog.askstring(
        "Nombre del estudiante",
        "Ingresa tu nombre y apellido sin espacios:\n(Ej: AndieBarreno)",
        parent=root
    )
    if not nombre_apellido or not nombre_apellido.strip():
        print("Operacion cancelada.")
        sys.exit(0)

    root.destroy()
    return origen, nombre_apellido.strip()


def main():
    args = sys.argv[1:]

    if len(args) >= 2:
        origen = args[0]
        nombre_apellido = args[1]
    else:
        try:
            origen, nombre_apellido = pedir_datos_con_ventana()
        except Exception:
            print("=== Analizador Lexico y Sintactico C++ ===\n")
            origen = input("Nombre del archivo .cpp: ").strip()
            nombre_apellido = input("Tu nombre y apellido sin espacios: ").strip()

    if not os.path.isfile(origen):
        print(f"Error: no se encontro el archivo '{origen}'")
        sys.exit(1)

    with open(origen, "r", encoding="utf-8") as f:
        codigo = f.read()

    # --- Fase lexica ---
    tokens_result, errores_lex = analizar_lexico(codigo)
    print(f"\n[LEXICO] {len(tokens_result)} tokens | {len(errores_lex)} errores")
    for tipo, valor, linea in tokens_result:
        print(f"  L{linea}: {tipo:<18} -> {valor}")
    if errores_lex:
        print("\nErrores lexicos:")
        for e in errores_lex:
            print(" -", e)
    ruta_lex = generar_log("lexico", nombre_apellido, codigo, tokens_result, errores_lex)
    print(f"\nLog lexico generado: {ruta_lex}")

    # --- Fase sintactica ---
    _, errores_sint = analizar_sintactico(codigo)
    print(f"\n[SINTACTICO] {len(errores_sint)} errores")
    if errores_sint:
        for e in errores_sint:
            print(" -", e)
    else:
        print("  El programa es sintacticamente VALIDO.")
    ruta_sint = generar_log("sintactico", nombre_apellido, codigo, [], errores_sint)
    print(f"Log sintactico generado: {ruta_sint}")


if __name__ == "__main__":
    main()
