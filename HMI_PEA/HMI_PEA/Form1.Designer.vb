<Global.Microsoft.VisualBasic.CompilerServices.DesignerGenerated()> _
Partial Class Form1
    Inherits System.Windows.Forms.Form

    'Form overrides dispose to clean up the component list.
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

    'Required by the Windows Form Designer
    Private components As System.ComponentModel.IContainer

    'NOTE: The following procedure is required by the Windows Form Designer
    'It can be modified using the Windows Form Designer.  
    'Do not modify it using the code editor.
    <System.Diagnostics.DebuggerStepThrough()> _
    Private Sub InitializeComponent()
        Me.components = New System.ComponentModel.Container()
        Me.Panel1 = New System.Windows.Forms.Panel()
        Me.Label1 = New System.Windows.Forms.Label()
        Me.Tab_Configuração = New System.Windows.Forms.TabPage()
        Me.btnGuardarPadrao = New System.Windows.Forms.Button()
        Me.Label14 = New System.Windows.Forms.Label()
        Me.Label13 = New System.Windows.Forms.Label()
        Me.picImagemPadrao_Config = New System.Windows.Forms.PictureBox()
        Me.picImagemAtual_Config = New System.Windows.Forms.PictureBox()
        Me.Tab_Manual = New System.Windows.Forms.TabPage()
        Me.txtCieY = New System.Windows.Forms.TextBox()
        Me.txtCieX = New System.Windows.Forms.TextBox()
        Me.txtLuminosidade = New System.Windows.Forms.TextBox()
        Me.Label8 = New System.Windows.Forms.Label()
        Me.Label7 = New System.Windows.Forms.Label()
        Me.Label5 = New System.Windows.Forms.Label()
        Me.GroupBox2 = New System.Windows.Forms.GroupBox()
        Me.VScrollBar1 = New System.Windows.Forms.VScrollBar()
        Me.txtAnaliseTecnica = New System.Windows.Forms.TextBox()
        Me.btnProcessarTeste = New System.Windows.Forms.Button()
        Me.btnCapturarImagem = New System.Windows.Forms.Button()
        Me.picImagemManual = New System.Windows.Forms.PictureBox()
        Me.Tab_Automatico = New System.Windows.Forms.TabPage()
        Me.GroupBox1 = New System.Windows.Forms.GroupBox()
        Me.lblRejeitadas = New System.Windows.Forms.Label()
        Me.lblAprovadas = New System.Windows.Forms.Label()
        Me.lblTotal = New System.Windows.Forms.Label()
        Me.lblStatusAuto = New System.Windows.Forms.Label()
        Me.picImagemAuto = New System.Windows.Forms.PictureBox()
        Me.TabControl1 = New System.Windows.Forms.TabControl()
        Me.TimerInspecao = New System.Windows.Forms.Timer(Me.components)
        Me.Panel1.SuspendLayout()
        Me.Tab_Configuração.SuspendLayout()
        CType(Me.picImagemPadrao_Config, System.ComponentModel.ISupportInitialize).BeginInit()
        CType(Me.picImagemAtual_Config, System.ComponentModel.ISupportInitialize).BeginInit()
        Me.Tab_Manual.SuspendLayout()
        Me.GroupBox2.SuspendLayout()
        CType(Me.picImagemManual, System.ComponentModel.ISupportInitialize).BeginInit()
        Me.Tab_Automatico.SuspendLayout()
        Me.GroupBox1.SuspendLayout()
        CType(Me.picImagemAuto, System.ComponentModel.ISupportInitialize).BeginInit()
        Me.TabControl1.SuspendLayout()
        Me.SuspendLayout()
        '
        'Panel1
        '
        Me.Panel1.BackColor = System.Drawing.Color.DarkBlue
        Me.Panel1.Controls.Add(Me.Label1)
        Me.Panel1.Dock = System.Windows.Forms.DockStyle.Top
        Me.Panel1.Location = New System.Drawing.Point(0, 0)
        Me.Panel1.Name = "Panel1"
        Me.Panel1.Size = New System.Drawing.Size(1038, 100)
        Me.Panel1.TabIndex = 0
        '
        'Label1
        '
        Me.Label1.AutoSize = True
        Me.Label1.BackColor = System.Drawing.Color.DarkBlue
        Me.Label1.Font = New System.Drawing.Font("Microsoft Sans Serif", 15.75!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.Label1.ForeColor = System.Drawing.SystemColors.ControlLight
        Me.Label1.Location = New System.Drawing.Point(320, 32)
        Me.Label1.Name = "Label1"
        Me.Label1.Size = New System.Drawing.Size(506, 25)
        Me.Label1.TabIndex = 0
        Me.Label1.Text = "SISTEMA DE VISÃO - CONTROLO DE QUALIDADE"
        '
        'Tab_Configuração
        '
        Me.Tab_Configuração.Controls.Add(Me.btnGuardarPadrao)
        Me.Tab_Configuração.Controls.Add(Me.Label14)
        Me.Tab_Configuração.Controls.Add(Me.Label13)
        Me.Tab_Configuração.Controls.Add(Me.picImagemPadrao_Config)
        Me.Tab_Configuração.Controls.Add(Me.picImagemAtual_Config)
        Me.Tab_Configuração.Location = New System.Drawing.Point(4, 34)
        Me.Tab_Configuração.Name = "Tab_Configuração"
        Me.Tab_Configuração.Padding = New System.Windows.Forms.Padding(3, 3, 3, 3)
        Me.Tab_Configuração.Size = New System.Drawing.Size(1030, 454)
        Me.Tab_Configuração.TabIndex = 2
        Me.Tab_Configuração.Text = "Configuração / Padrão"
        Me.Tab_Configuração.UseVisualStyleBackColor = True
        '
        'btnGuardarPadrao
        '
        Me.btnGuardarPadrao.FlatStyle = System.Windows.Forms.FlatStyle.Flat
        Me.btnGuardarPadrao.Font = New System.Drawing.Font("Microsoft Sans Serif", 14.25!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.btnGuardarPadrao.ForeColor = System.Drawing.Color.Orange
        Me.btnGuardarPadrao.Location = New System.Drawing.Point(828, 370)
        Me.btnGuardarPadrao.Name = "btnGuardarPadrao"
        Me.btnGuardarPadrao.Size = New System.Drawing.Size(188, 67)
        Me.btnGuardarPadrao.TabIndex = 5
        Me.btnGuardarPadrao.Text = "Definir Imagem Atual como Novo Padrão"
        Me.btnGuardarPadrao.UseVisualStyleBackColor = True
        '
        'Label14
        '
        Me.Label14.AutoSize = True
        Me.Label14.Font = New System.Drawing.Font("Microsoft Sans Serif", 14.25!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.Label14.Location = New System.Drawing.Point(550, 12)
        Me.Label14.Name = "Label14"
        Me.Label14.Size = New System.Drawing.Size(143, 24)
        Me.Label14.TabIndex = 3
        Me.Label14.Text = "Imagem Padrão"
        '
        'Label13
        '
        Me.Label13.AutoSize = True
        Me.Label13.Font = New System.Drawing.Font("Microsoft Sans Serif", 14.25!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.Label13.Location = New System.Drawing.Point(115, 12)
        Me.Label13.Name = "Label13"
        Me.Label13.Size = New System.Drawing.Size(125, 24)
        Me.Label13.TabIndex = 2
        Me.Label13.Text = "Imagem Atual"
        '
        'picImagemPadrao_Config
        '
        Me.picImagemPadrao_Config.Location = New System.Drawing.Point(425, 43)
        Me.picImagemPadrao_Config.Name = "picImagemPadrao_Config"
        Me.picImagemPadrao_Config.Size = New System.Drawing.Size(382, 402)
        Me.picImagemPadrao_Config.TabIndex = 1
        Me.picImagemPadrao_Config.TabStop = False
        '
        'picImagemAtual_Config
        '
        Me.picImagemAtual_Config.Location = New System.Drawing.Point(7, 43)
        Me.picImagemAtual_Config.Name = "picImagemAtual_Config"
        Me.picImagemAtual_Config.Size = New System.Drawing.Size(382, 402)
        Me.picImagemAtual_Config.TabIndex = 0
        Me.picImagemAtual_Config.TabStop = False
        '
        'Tab_Manual
        '
        Me.Tab_Manual.Controls.Add(Me.txtCieY)
        Me.Tab_Manual.Controls.Add(Me.txtCieX)
        Me.Tab_Manual.Controls.Add(Me.txtLuminosidade)
        Me.Tab_Manual.Controls.Add(Me.Label8)
        Me.Tab_Manual.Controls.Add(Me.Label7)
        Me.Tab_Manual.Controls.Add(Me.Label5)
        Me.Tab_Manual.Controls.Add(Me.GroupBox2)
        Me.Tab_Manual.Controls.Add(Me.btnProcessarTeste)
        Me.Tab_Manual.Controls.Add(Me.btnCapturarImagem)
        Me.Tab_Manual.Controls.Add(Me.picImagemManual)
        Me.Tab_Manual.Location = New System.Drawing.Point(4, 34)
        Me.Tab_Manual.Name = "Tab_Manual"
        Me.Tab_Manual.Padding = New System.Windows.Forms.Padding(3, 3, 3, 3)
        Me.Tab_Manual.Size = New System.Drawing.Size(1030, 454)
        Me.Tab_Manual.TabIndex = 1
        Me.Tab_Manual.Text = "Manual"
        Me.Tab_Manual.UseVisualStyleBackColor = True
        '
        'txtCieY
        '
        Me.txtCieY.Location = New System.Drawing.Point(429, 341)
        Me.txtCieY.Margin = New System.Windows.Forms.Padding(2, 2, 2, 2)
        Me.txtCieY.Name = "txtCieY"
        Me.txtCieY.Size = New System.Drawing.Size(146, 20)
        Me.txtCieY.TabIndex = 10
        '
        'txtCieX
        '
        Me.txtCieX.Location = New System.Drawing.Point(429, 268)
        Me.txtCieX.Margin = New System.Windows.Forms.Padding(2, 2, 2, 2)
        Me.txtCieX.Name = "txtCieX"
        Me.txtCieX.Size = New System.Drawing.Size(146, 20)
        Me.txtCieX.TabIndex = 9
        '
        'txtLuminosidade
        '
        Me.txtLuminosidade.Location = New System.Drawing.Point(429, 197)
        Me.txtLuminosidade.Margin = New System.Windows.Forms.Padding(2, 2, 2, 2)
        Me.txtLuminosidade.Name = "txtLuminosidade"
        Me.txtLuminosidade.Size = New System.Drawing.Size(146, 20)
        Me.txtLuminosidade.TabIndex = 8
        '
        'Label8
        '
        Me.Label8.AutoSize = True
        Me.Label8.Font = New System.Drawing.Font("Microsoft Sans Serif", 11.25!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.Label8.ForeColor = System.Drawing.SystemColors.ControlText
        Me.Label8.Location = New System.Drawing.Point(430, 316)
        Me.Label8.Name = "Label8"
        Me.Label8.Size = New System.Drawing.Size(103, 18)
        Me.Label8.TabIndex = 7
        Me.Label8.Text = "Coordenada Y"
        '
        'Label7
        '
        Me.Label7.AutoSize = True
        Me.Label7.Font = New System.Drawing.Font("Microsoft Sans Serif", 11.25!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.Label7.ForeColor = System.Drawing.SystemColors.ControlText
        Me.Label7.Location = New System.Drawing.Point(428, 243)
        Me.Label7.Name = "Label7"
        Me.Label7.Size = New System.Drawing.Size(104, 18)
        Me.Label7.TabIndex = 6
        Me.Label7.Text = "Coordenada X"
        '
        'Label5
        '
        Me.Label5.AutoSize = True
        Me.Label5.Font = New System.Drawing.Font("Microsoft Sans Serif", 11.25!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.Label5.Location = New System.Drawing.Point(428, 173)
        Me.Label5.Name = "Label5"
        Me.Label5.Size = New System.Drawing.Size(151, 18)
        Me.Label5.TabIndex = 0
        Me.Label5.Text = "Intensidade Luminosa"
        '
        'GroupBox2
        '
        Me.GroupBox2.Controls.Add(Me.VScrollBar1)
        Me.GroupBox2.Controls.Add(Me.txtAnaliseTecnica)
        Me.GroupBox2.Font = New System.Drawing.Font("Microsoft Sans Serif", 12.0!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.GroupBox2.Location = New System.Drawing.Point(728, 25)
        Me.GroupBox2.Name = "GroupBox2"
        Me.GroupBox2.Size = New System.Drawing.Size(269, 415)
        Me.GroupBox2.TabIndex = 4
        Me.GroupBox2.TabStop = False
        Me.GroupBox2.Text = "Análise Técnica"
        '
        'VScrollBar1
        '
        Me.VScrollBar1.Dock = System.Windows.Forms.DockStyle.Right
        Me.VScrollBar1.Location = New System.Drawing.Point(249, 22)
        Me.VScrollBar1.Name = "VScrollBar1"
        Me.VScrollBar1.Size = New System.Drawing.Size(17, 390)
        Me.VScrollBar1.TabIndex = 1
        '
        'txtAnaliseTecnica
        '
        Me.txtAnaliseTecnica.Dock = System.Windows.Forms.DockStyle.Fill
        Me.txtAnaliseTecnica.Location = New System.Drawing.Point(3, 22)
        Me.txtAnaliseTecnica.Multiline = True
        Me.txtAnaliseTecnica.Name = "txtAnaliseTecnica"
        Me.txtAnaliseTecnica.Size = New System.Drawing.Size(263, 390)
        Me.txtAnaliseTecnica.TabIndex = 0
        '
        'btnProcessarTeste
        '
        Me.btnProcessarTeste.Font = New System.Drawing.Font("Microsoft Sans Serif", 14.25!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.btnProcessarTeste.ForeColor = System.Drawing.SystemColors.Highlight
        Me.btnProcessarTeste.Location = New System.Drawing.Point(430, 90)
        Me.btnProcessarTeste.Name = "btnProcessarTeste"
        Me.btnProcessarTeste.Size = New System.Drawing.Size(190, 40)
        Me.btnProcessarTeste.TabIndex = 3
        Me.btnProcessarTeste.Text = "Processar Teste"
        Me.btnProcessarTeste.UseVisualStyleBackColor = True
        '
        'btnCapturarImagem
        '
        Me.btnCapturarImagem.Font = New System.Drawing.Font("Microsoft Sans Serif", 14.25!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.btnCapturarImagem.ForeColor = System.Drawing.SystemColors.Highlight
        Me.btnCapturarImagem.Location = New System.Drawing.Point(430, 25)
        Me.btnCapturarImagem.Name = "btnCapturarImagem"
        Me.btnCapturarImagem.Size = New System.Drawing.Size(190, 40)
        Me.btnCapturarImagem.TabIndex = 2
        Me.btnCapturarImagem.Text = "Capturar Imagem"
        Me.btnCapturarImagem.UseVisualStyleBackColor = True
        '
        'picImagemManual
        '
        Me.picImagemManual.BorderStyle = System.Windows.Forms.BorderStyle.Fixed3D
        Me.picImagemManual.Location = New System.Drawing.Point(8, 6)
        Me.picImagemManual.Name = "picImagemManual"
        Me.picImagemManual.Size = New System.Drawing.Size(384, 435)
        Me.picImagemManual.SizeMode = System.Windows.Forms.PictureBoxSizeMode.Zoom
        Me.picImagemManual.TabIndex = 0
        Me.picImagemManual.TabStop = False
        '
        'Tab_Automatico
        '
        Me.Tab_Automatico.Controls.Add(Me.GroupBox1)
        Me.Tab_Automatico.Controls.Add(Me.lblStatusAuto)
        Me.Tab_Automatico.Controls.Add(Me.picImagemAuto)
        Me.Tab_Automatico.ForeColor = System.Drawing.Color.LightGray
        Me.Tab_Automatico.Location = New System.Drawing.Point(4, 34)
        Me.Tab_Automatico.Name = "Tab_Automatico"
        Me.Tab_Automatico.Padding = New System.Windows.Forms.Padding(3, 3, 3, 3)
        Me.Tab_Automatico.Size = New System.Drawing.Size(1030, 454)
        Me.Tab_Automatico.TabIndex = 0
        Me.Tab_Automatico.Text = "Automático"
        Me.Tab_Automatico.UseVisualStyleBackColor = True
        '
        'GroupBox1
        '
        Me.GroupBox1.Controls.Add(Me.lblRejeitadas)
        Me.GroupBox1.Controls.Add(Me.lblAprovadas)
        Me.GroupBox1.Controls.Add(Me.lblTotal)
        Me.GroupBox1.Font = New System.Drawing.Font("Microsoft Sans Serif", 12.0!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.GroupBox1.Location = New System.Drawing.Point(544, 117)
        Me.GroupBox1.Name = "GroupBox1"
        Me.GroupBox1.Size = New System.Drawing.Size(434, 324)
        Me.GroupBox1.TabIndex = 2
        Me.GroupBox1.TabStop = False
        Me.GroupBox1.Text = "Produção Atual"
        '
        'lblRejeitadas
        '
        Me.lblRejeitadas.AutoSize = True
        Me.lblRejeitadas.Font = New System.Drawing.Font("Microsoft Sans Serif", 11.25!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.lblRejeitadas.ForeColor = System.Drawing.Color.Black
        Me.lblRejeitadas.Location = New System.Drawing.Point(34, 137)
        Me.lblRejeitadas.Name = "lblRejeitadas"
        Me.lblRejeitadas.Size = New System.Drawing.Size(93, 18)
        Me.lblRejeitadas.TabIndex = 2
        Me.lblRejeitadas.Text = "Rejeitadas: 0"
        '
        'lblAprovadas
        '
        Me.lblAprovadas.AutoSize = True
        Me.lblAprovadas.Font = New System.Drawing.Font("Microsoft Sans Serif", 11.25!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.lblAprovadas.ForeColor = System.Drawing.Color.Black
        Me.lblAprovadas.Location = New System.Drawing.Point(34, 94)
        Me.lblAprovadas.Name = "lblAprovadas"
        Me.lblAprovadas.Size = New System.Drawing.Size(94, 18)
        Me.lblAprovadas.TabIndex = 1
        Me.lblAprovadas.Text = "Aprovadas: 0"
        '
        'lblTotal
        '
        Me.lblTotal.AutoSize = True
        Me.lblTotal.Font = New System.Drawing.Font("Microsoft Sans Serif", 11.25!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.lblTotal.ForeColor = System.Drawing.Color.Black
        Me.lblTotal.Location = New System.Drawing.Point(34, 50)
        Me.lblTotal.Name = "lblTotal"
        Me.lblTotal.Size = New System.Drawing.Size(149, 18)
        Me.lblTotal.TabIndex = 0
        Me.lblTotal.Text = "Total Inspecionado: 0"
        '
        'lblStatusAuto
        '
        Me.lblStatusAuto.Font = New System.Drawing.Font("Microsoft Sans Serif", 36.0!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.lblStatusAuto.Location = New System.Drawing.Point(544, 6)
        Me.lblStatusAuto.Name = "lblStatusAuto"
        Me.lblStatusAuto.Size = New System.Drawing.Size(434, 108)
        Me.lblStatusAuto.TabIndex = 1
        Me.lblStatusAuto.Text = "AGUARDANDO..."
        Me.lblStatusAuto.TextAlign = System.Drawing.ContentAlignment.MiddleCenter
        '
        'picImagemAuto
        '
        Me.picImagemAuto.BorderStyle = System.Windows.Forms.BorderStyle.Fixed3D
        Me.picImagemAuto.Location = New System.Drawing.Point(8, 6)
        Me.picImagemAuto.Name = "picImagemAuto"
        Me.picImagemAuto.Size = New System.Drawing.Size(423, 435)
        Me.picImagemAuto.SizeMode = System.Windows.Forms.PictureBoxSizeMode.Zoom
        Me.picImagemAuto.TabIndex = 0
        Me.picImagemAuto.TabStop = False
        '
        'TabControl1
        '
        Me.TabControl1.Controls.Add(Me.Tab_Automatico)
        Me.TabControl1.Controls.Add(Me.Tab_Manual)
        Me.TabControl1.Controls.Add(Me.Tab_Configuração)
        Me.TabControl1.Dock = System.Windows.Forms.DockStyle.Fill
        Me.TabControl1.ItemSize = New System.Drawing.Size(20, 30)
        Me.TabControl1.Location = New System.Drawing.Point(0, 100)
        Me.TabControl1.Name = "TabControl1"
        Me.TabControl1.SelectedIndex = 0
        Me.TabControl1.Size = New System.Drawing.Size(1038, 492)
        Me.TabControl1.TabIndex = 1
        '
        'TimerInspecao
        '
        '
        'Form1
        '
        Me.AutoScaleDimensions = New System.Drawing.SizeF(6.0!, 13.0!)
        Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
        Me.BackColor = System.Drawing.SystemColors.Control
        Me.ClientSize = New System.Drawing.Size(1038, 592)
        Me.Controls.Add(Me.TabControl1)
        Me.Controls.Add(Me.Panel1)
        Me.Name = "Form1"
        Me.Text = "Form1"
        Me.Panel1.ResumeLayout(False)
        Me.Panel1.PerformLayout()
        Me.Tab_Configuração.ResumeLayout(False)
        Me.Tab_Configuração.PerformLayout()
        CType(Me.picImagemPadrao_Config, System.ComponentModel.ISupportInitialize).EndInit()
        CType(Me.picImagemAtual_Config, System.ComponentModel.ISupportInitialize).EndInit()
        Me.Tab_Manual.ResumeLayout(False)
        Me.Tab_Manual.PerformLayout()
        Me.GroupBox2.ResumeLayout(False)
        Me.GroupBox2.PerformLayout()
        CType(Me.picImagemManual, System.ComponentModel.ISupportInitialize).EndInit()
        Me.Tab_Automatico.ResumeLayout(False)
        Me.GroupBox1.ResumeLayout(False)
        Me.GroupBox1.PerformLayout()
        CType(Me.picImagemAuto, System.ComponentModel.ISupportInitialize).EndInit()
        Me.TabControl1.ResumeLayout(False)
        Me.ResumeLayout(False)

    End Sub

    Friend WithEvents Panel1 As Panel
    Friend WithEvents Label1 As Label
    Friend WithEvents Tab_Configuração As TabPage
    Friend WithEvents btnGuardarPadrao As Button
    Friend WithEvents Label14 As Label
    Friend WithEvents Label13 As Label
    Friend WithEvents picImagemPadrao_Config As PictureBox
    Friend WithEvents picImagemAtual_Config As PictureBox
    Friend WithEvents Tab_Manual As TabPage
    Friend WithEvents Label8 As Label
    Friend WithEvents Label7 As Label
    Friend WithEvents Label5 As Label
    Friend WithEvents GroupBox2 As GroupBox
    Friend WithEvents VScrollBar1 As VScrollBar
    Friend WithEvents txtAnaliseTecnica As TextBox
    Friend WithEvents btnProcessarTeste As Button
    Friend WithEvents btnCapturarImagem As Button
    Friend WithEvents picImagemManual As PictureBox
    Friend WithEvents Tab_Automatico As TabPage
    Friend WithEvents GroupBox1 As GroupBox
    Friend WithEvents lblRejeitadas As Label
    Friend WithEvents lblAprovadas As Label
    Friend WithEvents lblTotal As Label
    Friend WithEvents lblStatusAuto As Label
    Friend WithEvents picImagemAuto As PictureBox
    Friend WithEvents TimerInspecao As Timer
    Friend WithEvents txtCieY As TextBox
    Friend WithEvents txtCieX As TextBox
    Friend WithEvents txtLuminosidade As TextBox
    Friend WithEvents TabControl1 As TabControl
End Class
