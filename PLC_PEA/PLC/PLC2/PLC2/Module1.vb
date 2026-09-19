Imports System.Net.Sockets

Module Module1

    ' ==========================================
    ' CONFIGURAÇÃO DO SERVIDOR PLC
    ' ==========================================
    Public PortaServidor As Integer = 5000

    ' ==========================================
    ' ESTADOS GLOBAIS
    ' ==========================================
    Public ServidorAtivo As Boolean = False
    Public ClienteLigado As Boolean = False
    Public SensorAtivo As Boolean = False

    ' ==========================================
    ' TOLERÂNCIAS GERAIS
    ' ==========================================
    Public ToleranciaMediaLum As Double = 0.7
    Public ToleranciaMinLum As Double = 0.7
    Public ToleranciaXY As Double = 0.015

End Module