"""
============================================================
 ANALIZADOR SINTACTICO PARA C++ (subconjunto del lenguaje)
 Proyecto: Implementacion de un Analizador Lexico, Sintactico
           y Semantico en C++
 Herramienta: PLY (Python Lex-Yacc) - modulo yacc

 Integrantes:
   - Andie Barreno     -> Declaracion de variables y expresiones
   - Gabriel Villao    -> Condicionales (if/else) y bucles (for, while)
   - Samuel Chichande  -> Funciones y clases
============================================================
"""

import ply.yacc as yacc
from lexer import tokens, lexer

# Lista global donde se acumulan los errores sintacticos
errores_sintacticos = []


# ============================================================
# PRECEDENCIA DE OPERADORES
# (de menor a mayor precedencia, el ultimo tiene mayor prioridad)
# Necesaria para resolver ambiguedades en expresiones aritmeticas
# y logicas — la definen en conjunto los 3 integrantes.
# ============================================================

precedence = (
    ('left',  'OR'),
    ('left',  'AND'),
    ('left',  'EQ', 'NEQ'),
    ('left',  'LT', 'GT', 'LE', 'GE'),
    ('left',  'PLUS', 'MINUS'),
    ('left',  'TIMES', 'DIVIDE', 'MOD'),
    ('right', 'NOT'),
    ('right', 'UMINUS'),         # menos unario  -x
    ('left',  'INCREMENT', 'DECREMENT'),
)


# ============================================================
# REGLA RAIZ — punto de entrada del programa
# ============================================================

def p_programa(p):
    '''programa : lista_sentencias'''
    p[0] = ('programa', p[1])


def p_lista_sentencias(p):
    '''lista_sentencias : lista_sentencias sentencia
                        | sentencia
                        | empty'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    elif len(p) == 2 and p[1] is not None:
        p[0] = [p[1]]
    else:
        p[0] = []


def p_sentencia(p):
    '''sentencia : sentencia_simple SEMICOLON
                 | bloque
                 | sentencia_if
                 | sentencia_while
                 | sentencia_for
                 | sentencia_do_while
                 | definicion_funcion
                 | definicion_clase
                 | directiva_include
                 | using_namespace
                 | sentencia_return SEMICOLON
                 | sentencia_cout SEMICOLON
                 | sentencia_cin SEMICOLON'''
    p[0] = p[1]


def p_bloque(p):
    '''bloque : LBRACE lista_sentencias RBRACE'''
    p[0] = ('bloque', p[2])


def p_empty(p):
    '''empty :'''
    p[0] = None


# ============================================================
# === INICIO APORTE: Andie Barreno
# === Declaracion de variables y expresiones aritmeticas/logicas
# ============================================================

# --- Tipos de dato reconocidos ---

def p_tipo(p):
    '''tipo : INT
            | FLOAT
            | DOUBLE
            | CHAR
            | BOOL
            | VOID
            | IDENTIFIER'''
    p[0] = ('tipo', p[1])


# --- Declaracion de variables ---
# Formas soportadas:
#   int x;
#   int x = 5;
#   int x, y;
#   int x = 5, y = 10;

def p_sentencia_simple_declaracion(p):
    '''sentencia_simple : tipo lista_declaradores'''
    p[0] = ('declaracion', p[1], p[2])


def p_lista_declaradores(p):
    '''lista_declaradores : lista_declaradores COMMA declarador
                          | declarador'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]


def p_declarador_simple(p):
    '''declarador : IDENTIFIER'''
    p[0] = ('declarador', p[1], None)


def p_declarador_con_valor(p):
    '''declarador : IDENTIFIER ASSIGN expresion'''
    p[0] = ('declarador', p[1], p[3])


def p_declarador_arreglo(p):
    '''declarador : IDENTIFIER LBRACKET expresion RBRACKET
                  | IDENTIFIER LBRACKET RBRACKET'''
    p[0] = ('declarador_arreglo', p[1])


# --- Asignacion simple (ya declarada previamente) ---
# Formas: x = 5;   x += 3;   x++;   x--;

def p_sentencia_simple_asignacion(p):
    '''sentencia_simple : IDENTIFIER ASSIGN expresion
                        | IDENTIFIER PLUS_ASSIGN expresion
                        | IDENTIFIER MINUS_ASSIGN expresion
                        | IDENTIFIER TIMES_ASSIGN expresion
                        | IDENTIFIER DIVIDE_ASSIGN expresion'''
    p[0] = ('asignacion', p[1], p[2], p[3])


# --- Expresiones ---
# Cubre: aritmeticas, logicas, relacionales, literales, llamadas a funcion

def p_expresion_binaria(p):
    '''expresion : expresion PLUS expresion
                 | expresion MINUS expresion
                 | expresion TIMES expresion
                 | expresion DIVIDE expresion
                 | expresion MOD expresion
                 | expresion EQ expresion
                 | expresion NEQ expresion
                 | expresion LT expresion
                 | expresion GT expresion
                 | expresion LE expresion
                 | expresion GE expresion
                 | expresion AND expresion
                 | expresion OR expresion'''
    p[0] = ('binaria', p[2], p[1], p[3])


def p_expresion_unaria(p):
    '''expresion : NOT expresion
                 | MINUS expresion %prec UMINUS'''
    p[0] = ('unaria', p[1], p[2])


def p_expresion_parentesis(p):
    '''expresion : LPAREN expresion RPAREN'''
    p[0] = p[2]


def p_expresion_numero(p):
    '''expresion : NUMBER_INT
                 | NUMBER_FLOAT'''
    p[0] = ('numero', p[1])


def p_expresion_string(p):
    '''expresion : STRING_LITERAL'''
    p[0] = ('string', p[1])


def p_expresion_char(p):
    '''expresion : CHAR_LITERAL'''
    p[0] = ('char', p[1])


def p_expresion_bool(p):
    '''expresion : TRUE
                 | FALSE'''
    p[0] = ('bool', p[1])


def p_expresion_identifier(p):
    '''expresion : IDENTIFIER'''
    p[0] = ('id', p[1])


def p_expresion_llamada(p):
    '''expresion : IDENTIFIER LPAREN lista_argumentos RPAREN'''
    p[0] = ('llamada', p[1], p[3])


def p_expresion_incremento(p):
    '''expresion : IDENTIFIER INCREMENT
                 | IDENTIFIER DECREMENT
                 | INCREMENT IDENTIFIER
                 | DECREMENT IDENTIFIER'''
    p[0] = ('incremento_expr', p[1], p[2])


def p_expresion_acceso_arreglo(p):
    '''expresion : IDENTIFIER LBRACKET expresion RBRACKET'''
    p[0] = ('acceso_arreglo', p[1], p[3])


def p_lista_argumentos(p):
    '''lista_argumentos : lista_argumentos COMMA expresion
                        | expresion
                        | empty'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    elif len(p) == 2 and p[1] is not None:
        p[0] = [p[1]]
    else:
        p[0] = []


# --- Directivas de preprocesador ---
# #include <iostream>  o  #include "archivo.h"
# El GT final es opcional para tolerar variaciones del archivo

def p_directiva_include(p):
    '''directiva_include : HASH INCLUDE LT IDENTIFIER GT
                         | HASH INCLUDE LT IDENTIFIER
                         | HASH INCLUDE STRING_LITERAL'''
    p[0] = ('include',)


# --- Expresion como sentencia ---
# Permite: 0;  x+1;  funcion();  (resultado descartado)
# Necesario porque C++ permite cualquier expresion como sentencia

def p_sentencia_simple_expresion(p):
    '''sentencia_simple : expresion'''
    p[0] = ('expr_sentencia', p[1])


def p_using_namespace(p):
    '''using_namespace : USING NAMESPACE IDENTIFIER SEMICOLON
                       | USING NAMESPACE STD SEMICOLON'''
    p[0] = ('using_namespace', p[3])


# --- Return ---

def p_sentencia_return(p):
    '''sentencia_return : RETURN expresion
                        | RETURN'''
    if len(p) == 3:
        p[0] = ('return', p[2])
    else:
        p[0] = ('return', None)


# ============================================================
# === FIN APORTE: Andie Barreno
# ============================================================


# ============================================================
# === INICIO APORTE: Gabriel Villao
# === Condicionales (if/else) y bucles (for, while, do-while)
# ============================================================

# --- if / else if / else ---
# Formas:
#   if (condicion) sentencia
#   if (condicion) { bloque }
#   if (condicion) { bloque } else { bloque }
#   if (condicion) { bloque } else if (...) { bloque }

def p_sentencia_if(p):
    '''sentencia_if : IF LPAREN expresion RPAREN bloque
                    | IF LPAREN expresion RPAREN bloque sentencia_else'''
    if len(p) == 6:
        p[0] = ('if', p[3], p[5], None)
    else:
        p[0] = ('if', p[3], p[5], p[6])


def p_sentencia_else(p):
    '''sentencia_else : ELSE bloque
                      | ELSE sentencia_if'''
    p[0] = ('else', p[2])


# --- while ---
# while (condicion) { bloque }

def p_sentencia_while(p):
    '''sentencia_while : WHILE LPAREN expresion RPAREN bloque'''
    p[0] = ('while', p[3], p[5])


# --- do-while ---
# do { bloque } while (condicion);

def p_sentencia_do_while(p):
    '''sentencia_do_while : DO bloque WHILE LPAREN expresion RPAREN SEMICOLON'''
    p[0] = ('do_while', p[2], p[5])


# --- for ---
# for (init; condicion; actualizacion) { bloque }
# Cubre:
#   for (int i = 0; i < 10; i++)
#   for (i = 0; i < 10; i++)
#   for (;;)  -> bucle infinito

def p_sentencia_for(p):
    '''sentencia_for : FOR LPAREN init_for SEMICOLON expresion_opt SEMICOLON actualizacion_for RPAREN bloque'''
    p[0] = ('for', p[3], p[5], p[7], p[9])


def p_init_for_declaracion(p):
    '''init_for : tipo IDENTIFIER ASSIGN expresion
                | tipo IDENTIFIER'''
    p[0] = ('init_decl', p[1], p[2])


def p_init_for_asignacion(p):
    '''init_for : IDENTIFIER ASSIGN expresion
                | empty'''
    p[0] = ('init_asig', p[1])


def p_expresion_opt(p):
    '''expresion_opt : expresion
                     | empty'''
    p[0] = p[1]


def p_actualizacion_for(p):
    '''actualizacion_for : IDENTIFIER INCREMENT
                         | IDENTIFIER DECREMENT
                         | INCREMENT IDENTIFIER
                         | DECREMENT IDENTIFIER
                         | IDENTIFIER ASSIGN expresion
                         | IDENTIFIER PLUS_ASSIGN expresion
                         | IDENTIFIER MINUS_ASSIGN expresion
                         | empty'''
    p[0] = ('actualizacion', p[1])


# --- switch / case / default ---
# switch (variable) { case valor: sentencias break; default: sentencias }

def p_sentencia_switch(p):
    '''sentencia : SWITCH LPAREN expresion RPAREN LBRACE lista_cases RBRACE'''
    p[0] = ('switch', p[3], p[6])


def p_lista_cases(p):
    '''lista_cases : lista_cases sentencia_case
                   | sentencia_case'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]


def p_sentencia_case(p):
    '''sentencia_case : CASE expresion COLON lista_sentencias BREAK SEMICOLON
                      | DEFAULT COLON lista_sentencias'''
    p[0] = ('case', p[2] if len(p) == 7 else 'default')


# --- cout / cin ---
# cout << "texto" << variable << endl;
# cin  >> variable;

def p_sentencia_cout(p):
    '''sentencia_cout : COUT lista_stream_out
                      | STD SCOPE COUT lista_stream_out'''
    p[0] = ('cout', p[2] if len(p) == 3 else p[4])


def p_lista_stream_out(p):
    '''lista_stream_out : lista_stream_out STREAM_OUT expresion
                        | lista_stream_out STREAM_OUT ENDL
                        | lista_stream_out STREAM_OUT STD SCOPE ENDL
                        | STREAM_OUT expresion
                        | STREAM_OUT ENDL
                        | STREAM_OUT STD SCOPE ENDL'''
    p[0] = ('stream_out',)


def p_sentencia_cin(p):
    '''sentencia_cin : CIN lista_stream_in
                     | STD SCOPE CIN lista_stream_in'''
    p[0] = ('cin',)


def p_lista_stream_in(p):
    '''lista_stream_in : lista_stream_in STREAM_IN IDENTIFIER
                       | STREAM_IN IDENTIFIER'''
    p[0] = ('stream_in',)


# ============================================================
# === FIN APORTE: Gabriel Villao
# ============================================================


# ============================================================
# === INICIO APORTE: Samuel Chichande
# === Funciones y clases
# ============================================================

# --- Definicion de funcion ---
# tipo nombre(parametros) { bloque }
# void saludar(string nombre) { ... }
# int sumar(int a, int b) { return a + b; }

def p_definicion_funcion(p):
    '''definicion_funcion : tipo IDENTIFIER LPAREN lista_parametros RPAREN bloque'''
    p[0] = ('funcion', p[1], p[2], p[4], p[6])


def p_lista_parametros(p):
    '''lista_parametros : lista_parametros COMMA parametro
                        | parametro
                        | empty'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    elif len(p) == 2 and p[1] is not None:
        p[0] = [p[1]]
    else:
        p[0] = []


def p_parametro(p):
    '''parametro : tipo IDENTIFIER
                 | tipo AMPERSAND IDENTIFIER
                 | tipo IDENTIFIER LBRACKET RBRACKET'''
    p[0] = ('parametro', p[1], p[len(p)-1])


# --- Llamada a funcion como sentencia ---
# funcion();
# funcion(arg1, arg2);

# --- Definicion de clase ---
# class Nombre { public: ... private: ... };

def p_definicion_clase(p):
    '''definicion_clase : CLASS IDENTIFIER LBRACE lista_miembros RBRACE SEMICOLON
                        | STRUCT IDENTIFIER LBRACE lista_miembros RBRACE SEMICOLON'''
    p[0] = ('clase', p[1], p[2], p[4])


def p_lista_miembros(p):
    '''lista_miembros : lista_miembros miembro
                      | miembro
                      | empty'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    elif len(p) == 2 and p[1] is not None:
        p[0] = [p[1]]
    else:
        p[0] = []


def p_miembro_seccion(p):
    '''miembro : PUBLIC COLON
               | PRIVATE COLON
               | PROTECTED COLON'''
    p[0] = ('seccion', p[1])


def p_miembro_atributo(p):
    '''miembro : tipo IDENTIFIER SEMICOLON
               | STATIC tipo IDENTIFIER SEMICOLON
               | CONST tipo IDENTIFIER SEMICOLON'''
    p[0] = ('atributo', p[1])


def p_miembro_metodo(p):
    '''miembro : tipo IDENTIFIER LPAREN lista_parametros RPAREN bloque
               | STATIC tipo IDENTIFIER LPAREN lista_parametros RPAREN bloque
               | tipo IDENTIFIER LPAREN lista_parametros RPAREN SEMICOLON'''
    p[0] = ('metodo', p[2])


# ============================================================
# === FIN APORTE: Samuel Chichande
# ============================================================


# ============================================================
# MANEJO DE ERRORES SINTACTICOS
# Comun a los 3 integrantes
# ============================================================

def p_sentencia_error(p):
    '''sentencia : error SEMICOLON
                 | error RBRACE'''
    # Recuperacion: al encontrar ; o } el parser se sincroniza
    # y sigue analizando el resto sin acumular errores en cascada
    p[0] = ('error_recuperado',)


def p_error(p):
    if p:
        msg = f"Error sintactico: token inesperado '{p.value}' (tipo: {p.type}) en la linea {p.lineno}"
    else:
        msg = "Error sintactico: fin de archivo inesperado"
    errores_sintacticos.append(msg)


# Construccion del parser
parser = yacc.yacc()
