Imports System.Globalization
Imports System.Linq

Public Class SegmentData
    Public Property XAtual As Double
    Public Property YAtual As Double
    Public Property LumAtual As Double

    Public Property XPadrao As Double
    Public Property YPadrao As Double
    Public Property LumPadrao As Double
End Class

Module PLCLogic

    Private UltimoIdPadrao As Integer = 0
    Private UltimosSegmentos As New List(Of SegmentData)

    Private UltimaMediaAtual As Double = 0
    Private UltimaMediaPadrao As Double = 0
    Private UltimoMinAtual As Double = 0
    Private UltimoMinPadrao As Double = 0
    Private UltimaDistanciaMaxXY As Double = 0

    Public Sub Reset()
        UltimoIdPadrao = 0
        UltimosSegmentos.Clear()

        UltimaMediaAtual = 0
        UltimaMediaPadrao = 0
        UltimoMinAtual = 0
        UltimoMinPadrao = 0
        UltimaDistanciaMaxXY = 0
    End Sub

    Public Function ProcessarMensagemAvaliacao(msg As String) As String
        Dim idPadrao As Integer = 0
        Dim segmentos As List(Of SegmentData) = Nothing

        If Not ExtrairDadosAvaliacao(msg, idPadrao, segmentos) Then
            Return "NOK"
        End If

        UltimoIdPadrao = idPadrao
        UltimosSegmentos = segmentos

        Return AvaliarSegmentos(segmentos)
    End Function

    Private Function ExtrairDadosAvaliacao(msg As String,
                                           ByRef idPadrao As Integer,
                                           ByRef segmentos As List(Of SegmentData)) As Boolean

        segmentos = New List(Of SegmentData)

        Try
            If String.IsNullOrWhiteSpace(msg) Then Return False
            If Not msg.StartsWith("AVALIAR|", StringComparison.OrdinalIgnoreCase) Then Return False

            Dim partes() As String = msg.Split("|"c)

            If partes.Length < 3 Then Return False

            If Not Integer.TryParse(partes(1), idPadrao) Then
                Return False
            End If

            For i As Integer = 2 To partes.Length - 1
                Dim bloco As String = partes(i).Trim()
                If bloco = "" Then Continue For

                Dim campos() As String = bloco.Split(";"c)
                If campos.Length <> 6 Then Return False

                Dim seg As New SegmentData()

                If Not Double.TryParse(campos(0).Replace(",", "."),
                                       NumberStyles.Any,
                                       CultureInfo.InvariantCulture,
                                       seg.XAtual) Then Return False

                If Not Double.TryParse(campos(1).Replace(",", "."),
                                       NumberStyles.Any,
                                       CultureInfo.InvariantCulture,
                                       seg.YAtual) Then Return False

                If Not Double.TryParse(campos(2).Replace(",", "."),
                                       NumberStyles.Any,
                                       CultureInfo.InvariantCulture,
                                       seg.LumAtual) Then Return False

                If Not Double.TryParse(campos(3).Replace(",", "."),
                                       NumberStyles.Any,
                                       CultureInfo.InvariantCulture,
                                       seg.XPadrao) Then Return False

                If Not Double.TryParse(campos(4).Replace(",", "."),
                                       NumberStyles.Any,
                                       CultureInfo.InvariantCulture,
                                       seg.YPadrao) Then Return False

                If Not Double.TryParse(campos(5).Replace(",", "."),
                                       NumberStyles.Any,
                                       CultureInfo.InvariantCulture,
                                       seg.LumPadrao) Then Return False

                segmentos.Add(seg)
            Next

            Return segmentos.Count > 0

        Catch
            Return False
        End Try
    End Function

    Private Function AvaliarSegmentos(segmentos As List(Of SegmentData)) As String

        If segmentos Is Nothing OrElse segmentos.Count = 0 Then
            Return "NOK"
        End If

        UltimaMediaAtual = segmentos.Average(Function(s) s.LumAtual)
        UltimaMediaPadrao = segmentos.Average(Function(s) s.LumPadrao)

        UltimoMinAtual = segmentos.Min(Function(s) s.LumAtual)
        UltimoMinPadrao = segmentos.Min(Function(s) s.LumPadrao)

        If UltimaMediaPadrao <= 0 OrElse UltimoMinPadrao <= 0 Then
            Return "NOK"
        End If

        Dim condicaoMedia As Boolean = (UltimaMediaAtual >= Module1.ToleranciaMediaLum * UltimaMediaPadrao)
        Dim condicaoMinimo As Boolean = (UltimoMinAtual >= Module1.ToleranciaMinLum * UltimoMinPadrao)

        Dim toleranciaXY As Double = Module1.ToleranciaXY
        Dim condicaoCor As Boolean = True

        UltimaDistanciaMaxXY = 0

        For Each seg In segmentos
            Dim dx As Double = seg.XAtual - seg.XPadrao
            Dim dy As Double = seg.YAtual - seg.YPadrao
            Dim distanciaXY As Double = Math.Sqrt(dx * dx + dy * dy)

            If distanciaXY > UltimaDistanciaMaxXY Then
                UltimaDistanciaMaxXY = distanciaXY
            End If

            If distanciaXY > toleranciaXY Then
                condicaoCor = False
            End If
        Next

        If condicaoMedia AndAlso condicaoMinimo AndAlso condicaoCor Then
            Return "OK"
        Else
            Return "NOK"
        End If
    End Function

    Public Function ObterUltimoIdPadrao() As Integer
        Return UltimoIdPadrao
    End Function

    Public Function ObterNumeroSegmentos() As Integer
        Return UltimosSegmentos.Count
    End Function

    Public Function ObterUltimaMediaAtual() As Double
        Return UltimaMediaAtual
    End Function

    Public Function ObterUltimaMediaPadrao() As Double
        Return UltimaMediaPadrao
    End Function

    Public Function ObterUltimoMinAtual() As Double
        Return UltimoMinAtual
    End Function

    Public Function ObterUltimoMinPadrao() As Double
        Return UltimoMinPadrao
    End Function

    Public Function ObterUltimaDistanciaMaxXY() As Double
        Return UltimaDistanciaMaxXY
    End Function

End Module