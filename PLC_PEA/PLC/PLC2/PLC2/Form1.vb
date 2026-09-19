Imports System.Net
Imports System.Net.Sockets
Imports System.Text
Imports System.Threading

Public Class Form1

    Private servidorPLC As TcpListener
    Private clienteRaspberry As TcpClient
    Private streamRaspberry As NetworkStream

    Private threadAceitar As Thread
    Private threadReceber As Thread

    Private simuladorServidor As Form2

    Private Sub Form1_Load(sender As Object, e As EventArgs) Handles MyBase.Load

        Module1.ServidorAtivo = False
        Module1.ClienteLigado = False
        Module1.SensorAtivo = False

        PLCLogic.Reset()

        btn_Connected.Text = "Conectar com o Servidor"
        btn_Connected.BackColor = Color.LightGreen

        btn_Send.Text = "Ativar Sensor"
        btn_Send.BackColor = Color.LightGreen

        AtualizarEstadoLigacao(False)
        AtualizarEstadoSensor(False)

        tb_Comunicacao.Clear()
        AdicionarComunicacao("PLC iniciado.")
        AdicionarComunicacao("Pronto para abrir servidor na porta " & Module1.PortaServidor & ".")

        tb_TolMediaLum.Text = Module1.ToleranciaMediaLum.ToString("F2")
        tb_TolMinLum.Text = Module1.ToleranciaMinLum.ToString("F2")
        tb_TolXY.Text = Module1.ToleranciaXY.ToString("F4")
    End Sub

    Private Sub btn_Connected_Click(sender As Object, e As EventArgs) Handles btn_Connected.Click
        If Module1.ServidorAtivo Then
            PararServidorPLC()
        Else
            IniciarServidorPLC()
        End If
    End Sub

    Private Sub btn_Send_Click(sender As Object, e As EventArgs) Handles btn_Send.Click
        Module1.SensorAtivo = Not Module1.SensorAtivo

        If Module1.SensorAtivo Then
            btn_Send.Text = "Desligar Sensor"
            btn_Send.BackColor = Color.IndianRed
            AtualizarEstadoSensor(True)
            AdicionarComunicacao("Sensor ativado.")
        Else
            btn_Send.Text = "Ativar Sensor"
            btn_Send.BackColor = Color.LightGreen
            AtualizarEstadoSensor(False)
            AdicionarComunicacao("Sensor desativado.")
        End If
    End Sub

    Private Sub btn_AbrirSimulador_Click(sender As Object, e As EventArgs) Handles btn_AbrirSimulador.Click
        If simuladorServidor Is Nothing OrElse simuladorServidor.IsDisposed Then
            simuladorServidor = New Form2()
            simuladorServidor.Show()
        Else
            simuladorServidor.BringToFront()
        End If
    End Sub

    Private Sub btn_LimparLog_Click(sender As Object, e As EventArgs) Handles btn_LimparLog.Click
        tb_Comunicacao.Clear()
    End Sub

    Private Sub btn_AplicarTolerancias_Click(sender As Object, e As EventArgs) Handles btn_AplicarTolerancias.Click

        Dim novaTolMedia As Double
        Dim novaTolMin As Double
        Dim novaTolXY As Double

        Dim txtMedia As String = tb_TolMediaLum.Text.Trim().Replace(",", ".")
        Dim txtMin As String = tb_TolMinLum.Text.Trim().Replace(",", ".")
        Dim txtXY As String = tb_TolXY.Text.Trim().Replace(",", ".")

        ' Validar tolerância da média luminosa
        If Not Double.TryParse(txtMedia, Globalization.NumberStyles.Any, Globalization.CultureInfo.InvariantCulture, novaTolMedia) Then
            MessageBox.Show("Valor inválido para a tolerância da média luminosa.",
                        "Erro",
                        MessageBoxButtons.OK,
                        MessageBoxIcon.Warning)
            Exit Sub
        End If

        ' Validar tolerância do mínimo luminoso
        If Not Double.TryParse(txtMin, Globalization.NumberStyles.Any, Globalization.CultureInfo.InvariantCulture, novaTolMin) Then
            MessageBox.Show("Valor inválido para a tolerância do mínimo luminoso.",
                        "Erro",
                        MessageBoxButtons.OK,
                        MessageBoxIcon.Warning)
            Exit Sub
        End If

        ' Validar tolerância XY
        If Not Double.TryParse(txtXY, Globalization.NumberStyles.Any, Globalization.CultureInfo.InvariantCulture, novaTolXY) Then
            MessageBox.Show("Valor inválido para a tolerância XY.",
                        "Erro",
                        MessageBoxButtons.OK,
                        MessageBoxIcon.Warning)
            Exit Sub
        End If

        ' Regras de validação
        If novaTolMedia <= 0 OrElse novaTolMedia > 1 Then
            MessageBox.Show("A tolerância da média luminosa deve estar entre 0 e 1.",
                        "Erro",
                        MessageBoxButtons.OK,
                        MessageBoxIcon.Warning)
            Exit Sub
        End If

        If novaTolMin <= 0 OrElse novaTolMin > 1 Then
            MessageBox.Show("A tolerância do mínimo luminoso deve estar entre 0 e 1.",
                        "Erro",
                        MessageBoxButtons.OK,
                        MessageBoxIcon.Warning)
            Exit Sub
        End If

        If novaTolXY <= 0 OrElse novaTolXY > 0.1 Then
            MessageBox.Show("A tolerância XY deve estar entre 0 e 0,1.",
                        "Erro",
                        MessageBoxButtons.OK,
                        MessageBoxIcon.Warning)
            Exit Sub
        End If

        ' Guardar os valores
        Module1.ToleranciaMediaLum = novaTolMedia
        Module1.ToleranciaMinLum = novaTolMin
        Module1.ToleranciaXY = novaTolXY

        ' Reescrever nas textboxes com formato consistente
        tb_TolMediaLum.Text = Module1.ToleranciaMediaLum.ToString("F2")
        tb_TolMinLum.Text = Module1.ToleranciaMinLum.ToString("F2")
        tb_TolXY.Text = Module1.ToleranciaXY.ToString("F4")

        AdicionarComunicacao("Tolerâncias atualizadas.")
        AdicionarComunicacao("Tolerância Média Lum: " & Module1.ToleranciaMediaLum.ToString("F2"))
        AdicionarComunicacao("Tolerância Mínimo Lum: " & Module1.ToleranciaMinLum.ToString("F2"))
        AdicionarComunicacao("Tolerância XY: " & Module1.ToleranciaXY.ToString("F4"))

    End Sub
    Private Sub IniciarServidorPLC()
        Try
            servidorPLC = New TcpListener(IPAddress.Any, Module1.PortaServidor)
            servidorPLC.Start()

            Module1.ServidorAtivo = True

            btn_Connected.Text = "Desconectar com o Servidor"
            btn_Connected.BackColor = Color.IndianRed

            AdicionarComunicacao("Servidor PLC iniciado na porta " & Module1.PortaServidor & ".")

            threadAceitar = New Thread(AddressOf AceitarClienteRaspberry)
            threadAceitar.IsBackground = True
            threadAceitar.Start()

        Catch ex As Exception
            Module1.ServidorAtivo = False
            AdicionarComunicacao("Erro ao iniciar servidor: " & ex.Message)

            MessageBox.Show("Erro ao iniciar servidor PLC: " & ex.Message,
                        "Erro",
                        MessageBoxButtons.OK,
                        MessageBoxIcon.Error)
        End Try
    End Sub

    Private Sub PararServidorPLC()
        Try
            Module1.ServidorAtivo = False
            Module1.ClienteLigado = False

            If streamRaspberry IsNot Nothing Then streamRaspberry.Close()
            If clienteRaspberry IsNot Nothing Then clienteRaspberry.Close()
            If servidorPLC IsNot Nothing Then servidorPLC.Stop()

        Catch
        End Try

        btn_Connected.Text = "Conectar com o Servidor"
        btn_Connected.BackColor = Color.LightGreen

        AtualizarEstadoLigacao(False)

        PLCLogic.Reset()

        AdicionarComunicacao("Servidor PLC parado.")
    End Sub

    Private Sub AceitarClienteRaspberry()
        Try
            While Module1.ServidorAtivo

                AdicionarComunicacao("A aguardar ligação do Raspberry...")

                clienteRaspberry = servidorPLC.AcceptTcpClient()
                streamRaspberry = clienteRaspberry.GetStream()

                Module1.ClienteLigado = True
                AtualizarEstadoLigacao(True)

                Dim endpoint As String = clienteRaspberry.Client.RemoteEndPoint.ToString()
                AdicionarComunicacao("Ligação TCP estabelecida com: " & endpoint)

                ' Processa esta ligação até ela fechar
                ReceberMensagensRaspberry()

                ' Quando sair da função de receção, fecha a ligação atual
                Try
                    If streamRaspberry IsNot Nothing Then streamRaspberry.Close()
                    If clienteRaspberry IsNot Nothing Then clienteRaspberry.Close()
                Catch
                End Try

                Module1.ClienteLigado = False
                AtualizarEstadoLigacao(False)
                AdicionarComunicacao("Ligação com o Raspberry terminada.")
            End While

        Catch ex As Exception
            If Module1.ServidorAtivo Then
                AdicionarComunicacao("Erro ao aceitar cliente Raspberry: " & ex.Message)
            End If
        End Try
    End Sub

    Private Sub ReceberMensagensRaspberry()
        Try
            Dim buffer(8191) As Byte

            While Module1.ServidorAtivo AndAlso Module1.ClienteLigado
                If streamRaspberry Is Nothing Then Exit While
                If Not streamRaspberry.CanRead Then Exit While

                Dim bytesLidos As Integer = streamRaspberry.Read(buffer, 0, buffer.Length)

                If bytesLidos <= 0 Then Exit While

                Dim msg As String = Encoding.UTF8.GetString(buffer, 0, bytesLidos).Trim()

                If msg <> "" Then
                    ProcessarMensagemRaspberry(msg)
                End If
            End While

        Catch ex As Exception
            If Module1.ServidorAtivo AndAlso Module1.ClienteLigado Then
                AdicionarComunicacao("Erro na receção: " & ex.Message)
            End If
        End Try
    End Sub

    Private Sub ProcessarMensagemRaspberry(msg As String)

        If Me.InvokeRequired Then
            Me.Invoke(Sub() ProcessarMensagemRaspberry(msg))
            Return
        End If

        AdicionarComunicacao("Recebido: " & msg)

        If msg.StartsWith("AVALIAR|", StringComparison.OrdinalIgnoreCase) Then

            AdicionarComunicacao("A processar avaliação...")

            Dim resultado As String = PLCLogic.ProcessarMensagemAvaliacao(msg)

            AdicionarComunicacao("ID do padrão: " & PLCLogic.ObterUltimoIdPadrao().ToString())
            AdicionarComunicacao("Total de segmentos recebidos: " & PLCLogic.ObterNumeroSegmentos().ToString())
            AdicionarComunicacao("Média peça: " & PLCLogic.ObterUltimaMediaAtual().ToString("F2"))
            AdicionarComunicacao("Média padrão: " & PLCLogic.ObterUltimaMediaPadrao().ToString("F2"))
            AdicionarComunicacao("Mínimo peça: " & PLCLogic.ObterUltimoMinAtual().ToString("F2"))
            AdicionarComunicacao("Mínimo padrão: " & PLCLogic.ObterUltimoMinPadrao().ToString("F2"))
            AdicionarComunicacao("Maior distância XY: " & PLCLogic.ObterUltimaDistanciaMaxXY().ToString("F4"))
            AdicionarComunicacao("Tolerância Média Lum usada: " & Module1.ToleranciaMediaLum.ToString("F2"))
            AdicionarComunicacao("Tolerância Mínimo Lum usada: " & Module1.ToleranciaMinLum.ToString("F2"))
            AdicionarComunicacao("Tolerância XY usada: " & Module1.ToleranciaXY.ToString("F4"))
            AdicionarComunicacao("Resultado calculado: " & resultado)

            EnviarResposta(resultado)

        Else
            AdicionarComunicacao("Mensagem não reconhecida pelo PLC.")
        End If

    End Sub

    Private Sub EnviarResposta(msg As String)
        Try
            If clienteRaspberry IsNot Nothing AndAlso clienteRaspberry.Connected AndAlso
               streamRaspberry IsNot Nothing AndAlso streamRaspberry.CanWrite Then

                Dim dados As Byte() = Encoding.UTF8.GetBytes(msg)
                streamRaspberry.Write(dados, 0, dados.Length)
                streamRaspberry.Flush()

                AdicionarComunicacao("Enviado: " & msg)
            Else
                AdicionarComunicacao("Não foi possível enviar resposta ao Raspberry.")
            End If

        Catch ex As Exception
            AdicionarComunicacao("Erro ao enviar resposta: " & ex.Message)
        End Try
    End Sub

    Private Sub AtualizarEstadoLigacao(ligado As Boolean)
        If Me.InvokeRequired Then
            Me.Invoke(Sub() AtualizarEstadoLigacao(ligado))
            Return
        End If

        If ligado Then
            lbl_EstadoLigacao.Text = "Ligado"
            lbl_EstadoLigacao.BackColor = Color.LightGreen
            lbl_EstadoLigacao.ForeColor = Color.Black
        Else
            lbl_EstadoLigacao.Text = "Desligado"
            lbl_EstadoLigacao.BackColor = Color.IndianRed
            lbl_EstadoLigacao.ForeColor = Color.White
        End If
    End Sub

    Private Sub AtualizarEstadoSensor(ativo As Boolean)
        If ativo Then
            lbl_EstadoSensor.Text = "Ativado"
            lbl_EstadoSensor.BackColor = Color.LightGreen
            lbl_EstadoSensor.ForeColor = Color.Black
        Else
            lbl_EstadoSensor.Text = "Desativado"
            lbl_EstadoSensor.BackColor = Color.IndianRed
            lbl_EstadoSensor.ForeColor = Color.White
        End If
    End Sub

    Private Sub AdicionarComunicacao(msg As String)
        If Me.InvokeRequired Then
            Me.Invoke(Sub() AdicionarComunicacao(msg))
            Return
        End If

        tb_Comunicacao.AppendText(
            DateTime.Now.ToString("HH:mm:ss") &
            " - " & msg &
            Environment.NewLine
        )
    End Sub

    Private Sub Form1_FormClosing(sender As Object, e As FormClosingEventArgs) Handles MyBase.FormClosing
        PararServidorPLC()
    End Sub

End Class