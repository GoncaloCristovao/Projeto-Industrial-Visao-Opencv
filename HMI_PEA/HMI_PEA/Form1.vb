Imports System.Net.Sockets
Imports System.Text
Imports System.IO
Imports System.Threading.Tasks

Public Class Form1
    ' ========================================================================
    ' 1. VARIÁVEIS GLOBAIS (Ligação de Rede e Contadores)
    ' ========================================================================
    Private clienteTCP As TcpClient
    Private streamTCP As NetworkStream

    Private contTotal As Integer = 0
    Private contAprovadas As Integer = 0
    Private contRejeitadas As Integer = 0

    ' ========================================================================
    ' 2. INICIALIZAÇÃO E LIGAÇÃO (Ao abrir e fechar o programa)
    ' ========================================================================
    Private Sub Form1_Load(sender As Object, e As EventArgs) Handles MyBase.Load
        TimerInspecao.Interval = 1500 ' Velocidade do modo automático (1.5 seg)
        LigarAoServidor()
    End Sub

    Private Sub LigarAoServidor()
        Try
            clienteTCP = New TcpClient("127.0.0.1", 8080)
            streamTCP = clienteTCP.GetStream()
            TimerInspecao.Start()
            lblStatusAuto.Text = "LIGADO AO PYTHON"
            lblStatusAuto.ForeColor = Color.Blue
        Catch ex As Exception
            lblStatusAuto.Text = "ERRO LIGAÇÃO"
            lblStatusAuto.ForeColor = Color.Orange
        End Try
    End Sub

    Private Sub Form1_FormClosing(sender As Object, e As FormClosingEventArgs) Handles MyBase.FormClosing
        TimerInspecao.Stop()
        If streamTCP IsNot Nothing Then streamTCP.Close()
        If clienteTCP IsNot Nothing Then clienteTCP.Close()
    End Sub

    ' ========================================================================
    ' 3. MODO AUTOMÁTICO E VÍDEO EM DIRETO (Geridos pelo Timer)
    ' ========================================================================
    Private Async Sub TimerInspecao_Tick(sender As Object, e As EventArgs) Handles TimerInspecao.Tick
        ' 1. Aba Automático (Inspeciona e conta peças)
        If TabControl1.SelectedTab Is Tab_Automatico Then
            TimerInspecao.Stop()
            Await ExecutarTesteAutomatico()
            TimerInspecao.Start()

            ' 2. Aba Configuração (Apenas pede a foto crua para vídeo em direto)
            ' NOTA: Escrito exatamente como estava nas suas propriedades
        ElseIf TabControl1.SelectedTab Is Tab_Configuração Then
            TimerInspecao.Stop()
            Await AtualizarLiveFeedConfig()
            TimerInspecao.Start()
        End If
    End Sub

    Private Async Function ExecutarTesteAutomatico() As Task
        If clienteTCP Is Nothing OrElse Not clienteTCP.Connected Then Return

        Try
            Dim msg As Byte() = Encoding.UTF8.GetBytes("AUTO")
            Await streamTCP.WriteAsync(msg, 0, msg.Length)

            Dim cabecalho As String = Await LerCabecalho()
            Dim partes() As String = cabecalho.Split("|"c)

            If partes.Length >= 3 AndAlso partes(0) = "AUTO" Then
                Dim status As String = partes(1)
                Dim tamanho As Integer = Convert.ToInt32(partes(2))

                Dim bufferImg As Byte() = Await LerImagem(tamanho)
                AtualizarPictureBox(picImagemAuto, bufferImg)

                AtualizarContadores(status)
            End If
        Catch ex As Exception
            lblStatusAuto.Text = "FALHA REDE"
        End Try
    End Function

    Private Async Function AtualizarLiveFeedConfig() As Task
        If clienteTCP Is Nothing OrElse Not clienteTCP.Connected Then Return

        Try
            Dim msg As Byte() = Encoding.UTF8.GetBytes("CAPTURAR")
            Await streamTCP.WriteAsync(msg, 0, msg.Length)

            Dim cabecalho As String = Await LerCabecalho()
            Dim partes() As String = cabecalho.Split("|"c)

            If partes.Length >= 3 AndAlso (partes(0) = "AUTO" Or partes(0) = "CAPTURAR") Then
                Dim tamanhoImagem As Integer = Convert.ToInt32(partes(2))
                Dim bufferImagem As Byte() = Await LerImagem(tamanhoImagem)

                AtualizarPictureBox(picImagemAtual_Config, bufferImagem)
            End If
        Catch ex As Exception
            ' Ignora falhas de rede no live feed
        End Try
    End Function

    Private Sub AtualizarContadores(status As String)
        contTotal += 1
        If status = "OK" Then
            contAprovadas += 1
            lblStatusAuto.Text = "PEÇA OK"
            lblStatusAuto.ForeColor = Color.LimeGreen
        Else
            contRejeitadas += 1
            lblStatusAuto.Text = "PEÇA NOK"
            lblStatusAuto.ForeColor = Color.Red
        End If

        lblTotal.Text = "Total Inspecionado: " & contTotal.ToString()
        lblAprovadas.Text = "Aprovadas: " & contAprovadas.ToString()
        lblRejeitadas.Text = "Rejeitadas: " & contRejeitadas.ToString()
    End Sub

    ' ========================================================================
    ' 4. MODO MANUAL (Acionado por Botões)
    ' ========================================================================
    Private Async Sub btnCapturarImagem_Click(sender As Object, e As EventArgs) Handles btnCapturarImagem.Click
        If clienteTCP Is Nothing OrElse Not clienteTCP.Connected Then Return

        txtAnaliseTecnica.AppendText(DateTime.Now.ToString("HH:mm:ss") & " - Nova imagem capturada da câmara." & vbCrLf)
        txtAnaliseTecnica.AppendText("A aguardar processamento..." & vbCrLf)

        Try
            Dim msg As Byte() = Encoding.UTF8.GetBytes("CAPTURAR")
            Await streamTCP.WriteAsync(msg, 0, msg.Length)

            Dim cabecalho As String = Await LerCabecalho()
            Dim partes() As String = cabecalho.Split("|"c)

            If partes(0) = "AUTO" Or partes(0) = "CAPTURAR" Then
                Dim tamanho As Integer = Convert.ToInt32(partes(2))
                Dim bufferImg As Byte() = Await LerImagem(tamanho)
                AtualizarPictureBox(picImagemManual, bufferImg)

                txtLuminosidade.Text = "Aguardando..."
                txtCieX.Text = "-"
                txtCieY.Text = "-"
            End If
        Catch ex As Exception
            MessageBox.Show("Erro ao capturar a imagem manual.")
        End Try
    End Sub

    Private Async Sub btnProcessarTeste_Click(sender As Object, e As EventArgs) Handles btnProcessarTeste.Click
        If clienteTCP Is Nothing OrElse Not clienteTCP.Connected Then Return

        Try
            Dim msg As Byte() = Encoding.UTF8.GetBytes("PROCESSAR")
            Await streamTCP.WriteAsync(msg, 0, msg.Length)

            Dim cabecalho As String = Await LerCabecalho()
            Dim partes() As String = cabecalho.Split("|"c)

            If partes.Length >= 6 AndAlso partes(0) = "MANUAL" Then
                txtCieX.Text = partes(2)
                txtCieY.Text = partes(3)
                txtLuminosidade.Text = partes(4) & " %"

                Dim tamanho As Integer = Convert.ToInt32(partes(5))
                Dim bufferImg As Byte() = Await LerImagem(tamanho)
                AtualizarPictureBox(picImagemManual, bufferImg)

                ' Escreve no relatório
                txtAnaliseTecnica.AppendText(DateTime.Now.ToString("HH:mm:ss") & " - Processamento concluído." & vbCrLf)
                txtAnaliseTecnica.AppendText(" -> Intensidade medida: " & partes(4) & " (Limite: 120)" & vbCrLf)
                txtAnaliseTecnica.AppendText(" -> Coordenada X: " & partes(2) & vbCrLf)
                txtAnaliseTecnica.AppendText(" -> Resultado Final: " & partes(1) & vbCrLf)
                txtAnaliseTecnica.AppendText("----------------------------------------" & vbCrLf)
            End If
        Catch ex As Exception
            MessageBox.Show("Erro ao processar os dados matemáticos.")
        End Try
    End Sub

    ' ========================================================================
    ' 5. MODO CONFIGURAÇÃO / PADRÃO (Duplo clique no botão btnGuardarPadrao)
    ' ========================================================================
    Private Async Sub btnGuardarPadrao_Click(sender As Object, e As EventArgs) Handles btnGuardarPadrao.Click
        If clienteTCP Is Nothing OrElse Not clienteTCP.Connected Then
            MessageBox.Show("Não está ligado ao servidor Python!", "Aviso", MessageBoxButtons.OK, MessageBoxIcon.Warning)
            Return
        End If

        Try
            Dim msg As Byte() = Encoding.UTF8.GetBytes("PADRAO")
            Await streamTCP.WriteAsync(msg, 0, msg.Length)

            Dim cabecalho As String = Await LerCabecalho()
            Dim partes() As String = cabecalho.Split("|"c)

            If partes(0) = "PADRAO_OK" Then
                Dim tamanho As Integer = Convert.ToInt32(partes(1))
                Dim bufferImg As Byte() = Await LerImagem(tamanho)

                AtualizarPictureBox(picImagemPadrao_Config, bufferImg)
                MessageBox.Show("A imagem atual foi guardada como o novo Padrão Industrial com sucesso!", "Configuração", MessageBoxButtons.OK, MessageBoxIcon.Information)
            End If

        Catch ex As Exception
            MessageBox.Show("Erro técnico ao tentar guardar o padrão na câmara.")
        End Try
    End Sub

    ' ========================================================================
    ' 6. FUNÇÕES AUXILIARES (Para não repetir código)
    ' ========================================================================
    Private Async Function LerCabecalho() As Task(Of String)
        Dim buffer(128) As Byte
        Dim bytesLidos As Integer = Await streamTCP.ReadAsync(buffer, 0, buffer.Length)
        Return Encoding.UTF8.GetString(buffer, 0, bytesLidos).Trim()
    End Function

    Private Async Function LerImagem(tamanho As Integer) As Task(Of Byte())
        Dim buffer(tamanho - 1) As Byte
        Dim totalLido As Integer = 0
        While totalLido < tamanho
            totalLido += Await streamTCP.ReadAsync(buffer, totalLido, tamanho - totalLido)
        End While
        Return buffer
    End Function

    Private Sub AtualizarPictureBox(picBox As PictureBox, buffer As Byte())
        Using ms As New MemoryStream(buffer)
            Dim img As Image = Image.FromStream(ms)
            picBox.Image = New Bitmap(img)
            picBox.SizeMode = PictureBoxSizeMode.Zoom
        End Using
    End Sub

End Class