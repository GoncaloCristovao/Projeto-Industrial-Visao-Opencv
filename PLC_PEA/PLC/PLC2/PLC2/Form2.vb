Imports System.Net.Sockets
Imports System.IO
Imports System.Text
Imports System.Threading

Public Class Form2

    Private clientePLC As TcpClient
    Private streamPLC As NetworkStream
    Private readerPLC As StreamReader
    Private writerPLC As StreamWriter

    Private threadReceber As Thread

    Private ligadoAoPLC As Boolean = False

    Private Sub Form2_Load(sender As Object, e As EventArgs) Handles MyBase.Load

        AtualizarEstadoLigacao(False)

        tb_ComunicacaoRasp.Clear()
        AdicionarComunicacao("Form2 iniciado.")
        AdicionarComunicacao("Pronto para simular Raspberry Pi.")

    End Sub

    Private Sub btn_ConnectPLC_Click(sender As Object, e As EventArgs) Handles btn_ConnectPLC.Click
        If ligadoAoPLC Then
            DesligarDoPLC()
        Else
            LigarAoPLC()
        End If
    End Sub

    Private Sub LigarAoPLC()
        Try
            clientePLC = New TcpClient("127.0.0.1", 5000)
            streamPLC = clientePLC.GetStream()

            readerPLC = New StreamReader(streamPLC, Encoding.UTF8)
            writerPLC = New StreamWriter(streamPLC, Encoding.UTF8) With {
                .AutoFlush = True
            }

            ligadoAoPLC = True
            AtualizarEstadoLigacao(True)

            btn_ConnectPLC.Text = "Desconectar do PLC"
            btn_ConnectPLC.BackColor = Color.IndianRed

            AdicionarComunicacao("Ligação ao PLC estabelecida.")

            threadReceber = New Thread(AddressOf ReceberMensagensDoPLC)
            threadReceber.IsBackground = True
            threadReceber.Start()

        Catch ex As Exception
            ligadoAoPLC = False
            AtualizarEstadoLigacao(False)

            AdicionarComunicacao("Erro ao ligar ao PLC: " & ex.Message)

            MessageBox.Show("Não foi possível ligar ao PLC." & vbCrLf & ex.Message,
                            "Erro de Ligação",
                            MessageBoxButtons.OK,
                            MessageBoxIcon.Warning)
        End Try
    End Sub

    Private Sub DesligarDoPLC()
        Try
            ligadoAoPLC = False

            If writerPLC IsNot Nothing Then writerPLC.Close()
            If readerPLC IsNot Nothing Then readerPLC.Close()
            If streamPLC IsNot Nothing Then streamPLC.Close()
            If clientePLC IsNot Nothing Then clientePLC.Close()

        Catch
        End Try

        AtualizarEstadoLigacao(False)
        btn_ConnectPLC.Text = "Conectar ao PLC"
        btn_ConnectPLC.BackColor = Color.LightGreen

        AdicionarComunicacao("Ligação ao PLC terminada.")
    End Sub

    Private Sub ReceberMensagensDoPLC()
        Try
            While ligadoAoPLC
                Dim linha As String = readerPLC.ReadLine()

                If linha Is Nothing Then Exit While
                If linha.Trim() = "" Then Continue While

                AdicionarComunicacao("Recebido do PLC: " & linha.Trim())
            End While

        Catch ex As Exception
            If ligadoAoPLC Then
                AdicionarComunicacao("Erro na receção do PLC: " & ex.Message)
            End If
        End Try

        ligadoAoPLC = False

        If Me.InvokeRequired Then
            Me.Invoke(Sub()
                          AtualizarEstadoLigacao(False)
                          btn_ConnectPLC.Text = "Conectar ao PLC"
                          btn_ConnectPLC.BackColor = Color.LightGreen
                          AdicionarComunicacao("Comunicação com o PLC terminada.")
                      End Sub)
        Else
            AtualizarEstadoLigacao(False)
            btn_ConnectPLC.Text = "Conectar ao PLC"
            btn_ConnectPLC.BackColor = Color.LightGreen
            AdicionarComunicacao("Comunicação com o PLC terminada.")
        End If
    End Sub

    Private Sub EnviarMensagemAoPLC(msg As String)
        Try
            If clientePLC IsNot Nothing AndAlso clientePLC.Connected AndAlso
               writerPLC IsNot Nothing Then

                writerPLC.WriteLine(msg)
                AdicionarComunicacao("Enviado ao PLC: " & msg)
            Else
                AdicionarComunicacao("Comunicação com o PLC ainda não estabelecida.")
            End If

        Catch ex As Exception
            AdicionarComunicacao("Erro ao enviar para o PLC: " & ex.Message)
        End Try
    End Sub

    Private Sub btn_SendOK_Click(sender As Object, e As EventArgs) Handles btn_SendOK.Click
        Dim msg As String =
            "AVALIAR|1" &
            "|0.3291;0.3312;145.0;0.3280;0.3295;146.0" &
            "|0.3300;0.3300;148.2;0.3290;0.3300;149.0" &
            "|0.3285;0.3320;144.1;0.3275;0.3310;145.0" &
            "|0.3298;0.3305;146.5;0.3288;0.3299;147.2" &
            "|0.3301;0.3310;147.0;0.3292;0.3305;148.0" &
            "|0.3297;0.3308;145.8;0.3289;0.3301;146.5" &
            "|0.3293;0.3311;146.2;0.3283;0.3300;147.0" &
            "|0.3302;0.3307;147.1;0.3291;0.3299;148.3" &
            "|0.3294;0.3315;145.5;0.3285;0.3307;146.8" &
            "|0.3299;0.3309;146.7;0.3287;0.3302;147.5"

        EnviarMensagemAoPLC(msg)
    End Sub

    Private Sub btn_SendNOK_Click(sender As Object, e As EventArgs) Handles btn_SendNOK.Click
        Dim msg As String =
            "AVALIAR|1" &
            "|0.3600;0.3600;90.0;0.3280;0.3295;146.0" &
            "|0.3550;0.3580;92.2;0.3290;0.3300;149.0" &
            "|0.3520;0.3570;88.1;0.3275;0.3310;145.0" &
            "|0.3510;0.3560;91.5;0.3288;0.3299;147.2" &
            "|0.3500;0.3550;89.0;0.3292;0.3305;148.0" &
            "|0.3490;0.3540;87.8;0.3289;0.3301;146.5" &
            "|0.3480;0.3530;93.2;0.3283;0.3300;147.0" &
            "|0.3470;0.3520;90.1;0.3291;0.3299;148.3" &
            "|0.3460;0.3510;89.5;0.3285;0.3307;146.8" &
            "|0.3450;0.3500;88.7;0.3287;0.3302;147.5"

        EnviarMensagemAoPLC(msg)
    End Sub

    Private Sub btn_SendCustom_Click(sender As Object, e As EventArgs) Handles btn_SendCustom.Click
        Dim msg As String = tb_CustomMensagem.Text.Trim()

        If msg = "" Then
            AdicionarComunicacao("Mensagem personalizada vazia.")
            Exit Sub
        End If

        EnviarMensagemAoPLC(msg)
    End Sub

    Private Sub btn_LimparCustom_Click(sender As Object, e As EventArgs) Handles btn_LimparCustom.Click
        tb_CustomMensagem.Clear()
        tb_CustomMensagem.Focus()
        AdicionarComunicacao("Mensagem personalizada limpa.")
    End Sub

    Private Sub btn_LimparLog_Click(sender As Object, e As EventArgs) Handles btn_LimparLog.Click
        tb_ComunicacaoRasp.Clear()
    End Sub

    Private Sub AtualizarEstadoLigacao(ligado As Boolean)

        If Me.InvokeRequired Then
            Me.Invoke(Sub() AtualizarEstadoLigacao(ligado))
            Return
        End If

        If ligado Then
            lbl_EstadoLigacaoPLC.Text = "Ligado"
            lbl_EstadoLigacaoPLC.BackColor = Color.LightGreen
            lbl_EstadoLigacaoPLC.ForeColor = Color.Black
        Else
            lbl_EstadoLigacaoPLC.Text = "Desligado"
            lbl_EstadoLigacaoPLC.BackColor = Color.IndianRed
            lbl_EstadoLigacaoPLC.ForeColor = Color.White
        End If
    End Sub

    Private Sub AdicionarComunicacao(msg As String)

        If Me.InvokeRequired Then
            Me.Invoke(Sub() AdicionarComunicacao(msg))
            Return
        End If

        tb_ComunicacaoRasp.AppendText(
            DateTime.Now.ToString("HH:mm:ss") &
            " - " & msg &
            Environment.NewLine
        )
    End Sub

    Private Sub Form2_FormClosing(sender As Object, e As FormClosingEventArgs) Handles MyBase.FormClosing
        DesligarDoPLC()
    End Sub

End Class