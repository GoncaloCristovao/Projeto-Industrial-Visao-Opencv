<Global.Microsoft.VisualBasic.CompilerServices.DesignerGenerated()> _
Partial Class Form1
    Inherits System.Windows.Forms.Form

    'Descartar substituições de formulário para limpar a lista de componentes.
    <System.Diagnostics.DebuggerNonUserCode()> _
    Protected Overrides Sub Dispose(ByVal disposing As Boolean)
        Try
            If disposing AndAlso components IsNot Nothing Then
                components.Dispose()
            End If
        Finally
            MyBase.Dispose(disposing)
        End Try
    End Sub

    'Exigido pelo Windows Form Designer
    Private components As System.ComponentModel.IContainer

    'OBSERVAÇÃO: o procedimento a seguir é exigido pelo Windows Form Designer
    'Pode ser modificado usando o Windows Form Designer.  
    'Não o modifique usando o editor de códigos.
    <System.Diagnostics.DebuggerStepThrough()> _
    Private Sub InitializeComponent()
        Me.btn_Connected = New System.Windows.Forms.Button()
        Me.tb_Comunicacao = New System.Windows.Forms.TextBox()
        Me.Label1 = New System.Windows.Forms.Label()
        Me.btn_AbrirSimulador = New System.Windows.Forms.Button()
        Me.btn_LimparLog = New System.Windows.Forms.Button()
        Me.Label2 = New System.Windows.Forms.Label()
        Me.lbl_LigacaoTexto = New System.Windows.Forms.Label()
        Me.lbl_EstadoLigacao = New System.Windows.Forms.Label()
        Me.lbl_EstadoSensor = New System.Windows.Forms.Label()
        Me.lbl_SensorTexto = New System.Windows.Forms.Label()
        Me.btn_Send = New System.Windows.Forms.Button()
        Me.Label3 = New System.Windows.Forms.Label()
        Me.Label4 = New System.Windows.Forms.Label()
        Me.Label5 = New System.Windows.Forms.Label()
        Me.Label6 = New System.Windows.Forms.Label()
        Me.btn_AplicarTolerancias = New System.Windows.Forms.Button()
        Me.tb_TolMediaLum = New System.Windows.Forms.TextBox()
        Me.tb_TolMinLum = New System.Windows.Forms.TextBox()
        Me.tb_TolXY = New System.Windows.Forms.TextBox()
        Me.SuspendLayout()
        '
        'btn_Connected
        '
        Me.btn_Connected.Location = New System.Drawing.Point(52, 68)
        Me.btn_Connected.Name = "btn_Connected"
        Me.btn_Connected.Size = New System.Drawing.Size(167, 63)
        Me.btn_Connected.TabIndex = 0
        Me.btn_Connected.Text = "Conectar com o Servidor"
        Me.btn_Connected.UseVisualStyleBackColor = True
        '
        'tb_Comunicacao
        '
        Me.tb_Comunicacao.Location = New System.Drawing.Point(52, 200)
        Me.tb_Comunicacao.Multiline = True
        Me.tb_Comunicacao.Name = "tb_Comunicacao"
        Me.tb_Comunicacao.ReadOnly = True
        Me.tb_Comunicacao.ScrollBars = System.Windows.Forms.ScrollBars.Vertical
        Me.tb_Comunicacao.Size = New System.Drawing.Size(540, 207)
        Me.tb_Comunicacao.TabIndex = 3
        '
        'Label1
        '
        Me.Label1.AutoSize = True
        Me.Label1.Font = New System.Drawing.Font("Microsoft Sans Serif", 7.8!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.Label1.Location = New System.Drawing.Point(49, 180)
        Me.Label1.Name = "Label1"
        Me.Label1.Size = New System.Drawing.Size(101, 16)
        Me.Label1.TabIndex = 4
        Me.Label1.Text = "Comunicação"
        '
        'btn_AbrirSimulador
        '
        Me.btn_AbrirSimulador.Location = New System.Drawing.Point(425, 68)
        Me.btn_AbrirSimulador.Name = "btn_AbrirSimulador"
        Me.btn_AbrirSimulador.Size = New System.Drawing.Size(167, 63)
        Me.btn_AbrirSimulador.TabIndex = 5
        Me.btn_AbrirSimulador.Text = "Abrir Simulador de Servidor"
        Me.btn_AbrirSimulador.UseVisualStyleBackColor = True
        '
        'btn_LimparLog
        '
        Me.btn_LimparLog.Location = New System.Drawing.Point(425, 413)
        Me.btn_LimparLog.Name = "btn_LimparLog"
        Me.btn_LimparLog.Size = New System.Drawing.Size(167, 52)
        Me.btn_LimparLog.TabIndex = 10
        Me.btn_LimparLog.Text = "Limpar Comunicação"
        Me.btn_LimparLog.UseVisualStyleBackColor = True
        '
        'Label2
        '
        Me.Label2.AutoSize = True
        Me.Label2.Font = New System.Drawing.Font("Microsoft Sans Serif", 10.2!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.Label2.Location = New System.Drawing.Point(49, 48)
        Me.Label2.Name = "Label2"
        Me.Label2.Size = New System.Drawing.Size(148, 20)
        Me.Label2.TabIndex = 11
        Me.Label2.Text = "Controlo do PLC"
        '
        'lbl_LigacaoTexto
        '
        Me.lbl_LigacaoTexto.AutoSize = True
        Me.lbl_LigacaoTexto.Location = New System.Drawing.Point(619, 203)
        Me.lbl_LigacaoTexto.Name = "lbl_LigacaoTexto"
        Me.lbl_LigacaoTexto.Size = New System.Drawing.Size(139, 17)
        Me.lbl_LigacaoTexto.TabIndex = 12
        Me.lbl_LigacaoTexto.Text = "Ligação ao Servidor:"
        '
        'lbl_EstadoLigacao
        '
        Me.lbl_EstadoLigacao.BackColor = System.Drawing.Color.IndianRed
        Me.lbl_EstadoLigacao.ForeColor = System.Drawing.Color.White
        Me.lbl_EstadoLigacao.Location = New System.Drawing.Point(619, 235)
        Me.lbl_EstadoLigacao.Name = "lbl_EstadoLigacao"
        Me.lbl_EstadoLigacao.Size = New System.Drawing.Size(132, 44)
        Me.lbl_EstadoLigacao.TabIndex = 13
        Me.lbl_EstadoLigacao.Text = "Desligado"
        Me.lbl_EstadoLigacao.TextAlign = System.Drawing.ContentAlignment.MiddleCenter
        '
        'lbl_EstadoSensor
        '
        Me.lbl_EstadoSensor.BackColor = System.Drawing.Color.IndianRed
        Me.lbl_EstadoSensor.ForeColor = System.Drawing.Color.White
        Me.lbl_EstadoSensor.Location = New System.Drawing.Point(619, 351)
        Me.lbl_EstadoSensor.Name = "lbl_EstadoSensor"
        Me.lbl_EstadoSensor.Size = New System.Drawing.Size(132, 44)
        Me.lbl_EstadoSensor.TabIndex = 15
        Me.lbl_EstadoSensor.Text = "Desativado"
        Me.lbl_EstadoSensor.TextAlign = System.Drawing.ContentAlignment.MiddleCenter
        '
        'lbl_SensorTexto
        '
        Me.lbl_SensorTexto.AutoSize = True
        Me.lbl_SensorTexto.Location = New System.Drawing.Point(619, 319)
        Me.lbl_SensorTexto.Name = "lbl_SensorTexto"
        Me.lbl_SensorTexto.Size = New System.Drawing.Size(57, 17)
        Me.lbl_SensorTexto.TabIndex = 14
        Me.lbl_SensorTexto.Text = "Sensor:"
        '
        'btn_Send
        '
        Me.btn_Send.BackColor = System.Drawing.SystemColors.ButtonHighlight
        Me.btn_Send.Location = New System.Drawing.Point(243, 68)
        Me.btn_Send.Name = "btn_Send"
        Me.btn_Send.Size = New System.Drawing.Size(159, 63)
        Me.btn_Send.TabIndex = 2
        Me.btn_Send.Text = "Ativar Sensor"
        Me.btn_Send.UseVisualStyleBackColor = False
        '
        'Label3
        '
        Me.Label3.AutoSize = True
        Me.Label3.Font = New System.Drawing.Font("Microsoft Sans Serif", 10.2!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.Label3.Location = New System.Drawing.Point(49, 503)
        Me.Label3.Name = "Label3"
        Me.Label3.Size = New System.Drawing.Size(170, 20)
        Me.Label3.TabIndex = 16
        Me.Label3.Text = "Definir Tolerâncias"
        '
        'Label4
        '
        Me.Label4.AutoSize = True
        Me.Label4.Location = New System.Drawing.Point(50, 535)
        Me.Label4.Name = "Label4"
        Me.Label4.Size = New System.Drawing.Size(181, 17)
        Me.Label4.TabIndex = 17
        Me.Label4.Text = "Média Luminosidade (0 - 1)"
        '
        'Label5
        '
        Me.Label5.AutoSize = True
        Me.Label5.Location = New System.Drawing.Point(49, 577)
        Me.Label5.Name = "Label5"
        Me.Label5.Size = New System.Drawing.Size(187, 17)
        Me.Label5.TabIndex = 18
        Me.Label5.Text = "Mínimo Luminosidade (0 - 1)"
        '
        'Label6
        '
        Me.Label6.AutoSize = True
        Me.Label6.Location = New System.Drawing.Point(50, 621)
        Me.Label6.Name = "Label6"
        Me.Label6.Size = New System.Drawing.Size(132, 17)
        Me.Label6.TabIndex = 19
        Me.Label6.Text = "Máximo XY (0 - 0,1)"
        '
        'btn_AplicarTolerancias
        '
        Me.btn_AplicarTolerancias.Location = New System.Drawing.Point(425, 592)
        Me.btn_AplicarTolerancias.Name = "btn_AplicarTolerancias"
        Me.btn_AplicarTolerancias.Size = New System.Drawing.Size(167, 52)
        Me.btn_AplicarTolerancias.TabIndex = 20
        Me.btn_AplicarTolerancias.Text = "Aplicar Tolerâncias"
        Me.btn_AplicarTolerancias.UseVisualStyleBackColor = True
        '
        'tb_TolMediaLum
        '
        Me.tb_TolMediaLum.Location = New System.Drawing.Point(254, 535)
        Me.tb_TolMediaLum.Name = "tb_TolMediaLum"
        Me.tb_TolMediaLum.Size = New System.Drawing.Size(100, 23)
        Me.tb_TolMediaLum.TabIndex = 21
        '
        'tb_TolMinLum
        '
        Me.tb_TolMinLum.Location = New System.Drawing.Point(254, 577)
        Me.tb_TolMinLum.Name = "tb_TolMinLum"
        Me.tb_TolMinLum.Size = New System.Drawing.Size(100, 23)
        Me.tb_TolMinLum.TabIndex = 22
        '
        'tb_TolXY
        '
        Me.tb_TolXY.Location = New System.Drawing.Point(254, 621)
        Me.tb_TolXY.Name = "tb_TolXY"
        Me.tb_TolXY.Size = New System.Drawing.Size(100, 23)
        Me.tb_TolXY.TabIndex = 23
        '
        'Form1
        '
        Me.AutoScaleDimensions = New System.Drawing.SizeF(8.0!, 17.0!)
        Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
        Me.ClientSize = New System.Drawing.Size(800, 683)
        Me.Controls.Add(Me.tb_TolXY)
        Me.Controls.Add(Me.tb_TolMinLum)
        Me.Controls.Add(Me.tb_TolMediaLum)
        Me.Controls.Add(Me.btn_AplicarTolerancias)
        Me.Controls.Add(Me.Label6)
        Me.Controls.Add(Me.Label5)
        Me.Controls.Add(Me.Label4)
        Me.Controls.Add(Me.Label3)
        Me.Controls.Add(Me.lbl_EstadoSensor)
        Me.Controls.Add(Me.lbl_SensorTexto)
        Me.Controls.Add(Me.lbl_EstadoLigacao)
        Me.Controls.Add(Me.lbl_LigacaoTexto)
        Me.Controls.Add(Me.Label2)
        Me.Controls.Add(Me.btn_LimparLog)
        Me.Controls.Add(Me.btn_AbrirSimulador)
        Me.Controls.Add(Me.Label1)
        Me.Controls.Add(Me.tb_Comunicacao)
        Me.Controls.Add(Me.btn_Send)
        Me.Controls.Add(Me.btn_Connected)
        Me.Font = New System.Drawing.Font("Microsoft Sans Serif", 8.25!)
        Me.Name = "Form1"
        Me.Text = "Form1"
        Me.ResumeLayout(False)
        Me.PerformLayout()

    End Sub

    Friend WithEvents btn_Connected As Button
    Friend WithEvents tb_Comunicacao As TextBox
    Friend WithEvents Label1 As Label
    Friend WithEvents btn_AbrirSimulador As Button
    Friend WithEvents btn_LimparLog As Button
    Friend WithEvents Label2 As Label
    Friend WithEvents lbl_LigacaoTexto As Label
    Friend WithEvents lbl_EstadoLigacao As Label
    Friend WithEvents lbl_EstadoSensor As Label
    Friend WithEvents lbl_SensorTexto As Label
    Friend WithEvents btn_Send As Button
    Friend WithEvents Label3 As Label
    Friend WithEvents Label4 As Label
    Friend WithEvents Label5 As Label
    Friend WithEvents Label6 As Label
    Friend WithEvents btn_AplicarTolerancias As Button
    Friend WithEvents tb_TolMediaLum As TextBox
    Friend WithEvents tb_TolMinLum As TextBox
    Friend WithEvents tb_TolXY As TextBox
End Class
