// Algoritmo 2 de ejemplo para probar el analizador lexico
#include <iostream>
using namespace std;

int main() {
    int numero;
    int contador = 1;
    int suma = 0;
    float promedio;
    bool esPar = false;
    char opcion = 'S';

    cout << "Ingrese un numero: ";
    cin >> numero;

    if (numero > 0 && numero <= 100) {
        cout << "Numero dentro del rango" << endl;
    } else {
        cout << "Numero fuera del rango" << endl;
    }

    if (numero % 2 == 0) {
        esPar = true;
        cout << "El numero es par" << endl;
    } else {
        cout << "El numero es impar" << endl;
    }
// Suma de los numeros desde 1 hasta el numero ingresado
    while (contador <= numero) {
        suma += contador;
        contador++;
    }

    promedio = suma / numero;

    cout << "Suma: " << suma << endl;
    cout << "Promedio: " << promedio << endl;

    for (int i = 0; i < 3; i++) {
        cout << "Iteracion: " << i << endl;
    }

    if (opcion == 'S' || opcion == 's') {
        cout << "Proceso finalizado correctamente" << endl;
    }

    return 0;
}