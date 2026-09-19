<Global.Microsoft.VisualBasic.CompilerServices.DesignerGenerated()>
Partial Class Form2
    Inherits System.Windows.Forms.Form

    'Descartar substituições de formulário para limpar a lista de componentes.
    <System.Diagnostics.DebuggerNonUserCode()>
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
    <System.Diagnostics.DebuggerStepThrough()>
    Private Sub InitializeComponent()
        Me.btn_ConnectPLC = New System.Windows.Forms.Button()
        Me.btn_SendOK = New System.Windows.Forms.Button()
        Me.btn_SendNOK = New System.Windows.Forms.Button()
        Me.btn_SendCustom = New System.Windows.Forms.Button()
        Me.btn_LimparLog = New System.Windows.Forms.Button()
        Me.tb_ComunicacaoRasp = New System.Windows.Forms.TextBox()
        Me.Label1 = New System.Windows.Forms.Label()
        Me.Label2 = New System.Windows.Forms.Label()
        Me.Label3 = New System.Windows.Forms.Label()
        Me.tb_CustomMensagem = New System.Windows.Forms.TextBox()
        Me.Label4 = New System.Windows.Forms.Label()
        Me.lbl_EstadoLigacaoPLC = New System.Windows.Forms.Label()
        Me.Label6 = New System.Windows.Forms.Label()
        Me.btn_LimparCustom = New System.Windows.Forms.Button()
        Me.SuspendLayout()
        '
        'btn_ConnectPLC
        '
        Me.btn_ConnectPLC.Location = New System.Drawing.Point(44, 29)
        Me.btn_ConnectPLC.Name = "btn_ConnectPLC"
        Me.btn_ConnectPLC.Size = New System.Drawing.Size(154, 54)
        Me.btn_ConnectPLC.TabIndex = 0
        Me.btn_ConnectPLC.Text = "Conectar ao PLC"
        Me.btn_ConnectPLC.UseVisualStyleBackColor = True
        '
        'btn_SendOK
        '
        Me.btn_SendOK.Location = New System.Drawing.Point(44, 121)
        Me.btn_SendOK.Name = "btn_SendOK"
        Me.btn_SendOK.Size = New System.Drawing.Size(154, 53)
        Me.btn_SendOK.TabIndex = 2
        Me.btn_SendOK.Text = "Enviar Exemplo OK"
        Me.btn_SendOK.UseVisualStyleBackColor = True
        '
        'btn_SendNOK
        '
        Me.btn_SendNOK.Location = New System.Drawing.Point(211, 121)
        Me.btn_SendNOK.Name = "btn_SendNOK"
        Me.btn_SendNOK.Size = New System.Drawing.Size(154, 53)
        Me.btn_SendNOK.TabIndex = 3
        Me.btn_SendNOK.Text = "Enviar Exemplo NOK"
        Me.btn_SendNOK.UseVisualStyleBackColor = True
        '
        'btn_SendCustom
        '
        Me.btn_SendCustom.Location = New System.Drawing.Point(379, 121)
        Me.btn_SendCustom.Name = "btn_SendCustom"
        Me.btn_SendCustom.Size = New System.Drawing.Size(154, 53)
        Me.btn_SendCustom.TabIndex = 7
        Me.btn_SendCustom.Text = "Enviar Personalizado"
        Me.btn_SendCustom.UseVisualStyleBackColor = True
        '
        'btn_LimparLog
        '
        Me.btn_LimparLog.Location = New System.Drawing.Point(379, 503)
        Me.btn_LimparLog.Name = "btn_LimparLog"
        Me.btn_LimparLog.Size = New System.Drawing.Size(154, 53)
        Me.btn_LimparLog.TabIndex = 9
        Me.btn_LimparLog.Text = "Limpar Comunicação"
        Me.btn_LimparLog.UseVisualStyleBackColor = True
        '
        'tb_ComunicacaoRasp
        '
        Me.tb_ComunicacaoRasp.Location = New System.Drawing.Point(44, 302)
        Me.tb_ComunicacaoRasp.Multiline = True
        Me.tb_ComunicacaoRasp.Name = "tb_ComunicacaoRasp"
        Me.tb_ComunicacaoRasp.ReadOnly = True
        Me.tb_ComunicacaoRasp.ScrollBars = System.Windows.Forms.ScrollBars.Vertical
        Me.tb_ComunicacaoRasp.Size = New System.Drawing.Size(489, 195)
        Me.tb_ComunicacaoRasp.TabIndex = 10
        '
        'Label1
        '
        Me.Label1.AutoSize = True
        Me.Label1.Location = New System.Drawing.Point(44, 7)
        Me.Label1.Name = "Label1"
        Me.Label1.Size = New System.Drawing.Size(130, 16)
        Me.Label1.TabIndex = 11
        Me.Label1.Text = "Controlo do Servidor"
        '
        'Label2
        '
        Me.Label2.AutoSize = True
        Me.Label2.Location = New System.Drawing.Point(41, 102)
        Me.Label2.Name = "Label2"
        Me.Label2.Size = New System.Drawing.Size(176, 16)
        Me.Label2.TabIndex = 12
        Me.Label2.Text = "Enviar Mensagens de Teste"
        '
        'Label3
        '
        Me.Label3.AutoSize = True
        Me.Label3.Location = New System.Drawing.Point(44, 269)
        Me.Label3.Name = "Label3"
        Me.Label3.Size = New System.Drawing.Size(90, 16)
        Me.Label3.TabIndex = 13
        Me.Label3.Text = "Comunicação"
        '
        'tb_CustomMensagem
        '
        Me.tb_CustomMensagem.Location = New System.Drawing.Point(215, 217)
        Me.tb_CustomMensagem.Name = "tb_CustomMensagem"
        Me.tb_CustomMensagem.Size = New System.Drawing.Size(318, 22)
        Me.tb_CustomMensagem.TabIndex = 14
        '
        'Label4
        '
        Me.Label4.AutoSize = True
        Me.Label4.Location = New System.Drawing.Point(44, 217)
        Me.Label4.Name = "Label4"
        Me.Label4.Size = New System.Drawing.Size(165, 16)
        Me.Label4.TabIndex = 15
        Me.Label4.Text = "Mensagem Personalizada"
        '
        'lbl_EstadoLigacaoPLC
        '
        Me.lbl_EstadoLigacaoPLC.AutoSize = True
        Me.lbl_EstadoLigacaoPLC.Location = New System.Drawing.Point(376, 48)
        Me.lbl_EstadoLigacaoPLC.Name = "lbl_EstadoLigacaoPLC"
        Me.lbl_EstadoLigacaoPLC.Size = New System.Drawing.Size(70, 16)
        Me.lbl_EstadoLigacaoPLC.TabIndex = 17
        Me.lbl_EstadoLigacaoPLC.Text = "Desligado"
        '
        'Label6
        '
        Me.Label6.AutoSize = True
        Me.Label6.Location = New System.Drawing.Point(227, 48)
        Me.Label6.Name = "Label6"
        Me.Label6.Size = New System.Drawing.Size(121, 16)
        Me.Label6.TabIndex = 20
        Me.Label6.Text = "Estado da Ligação"
        '
        'btn_LimparCustom
        '
        Me.btn_LimparCustom.Location = New System.Drawing.Point(386, 245)
        Me.btn_LimparCustom.Name = "btn_LimparCustom"
        Me.btn_LimparCustom.Size = New System.Drawing.Size(147, 27)
        Me.btn_LimparCustom.TabIndex = 21
        Me.btn_LimparCustom.Text = "Limpar Mensagem"
        Me.btn_LimparCustom.UseVisualStyleBackColor = True
        '
        'Form2
        '
        Me.AutoScaleDimensions = New System.Drawing.SizeF(8.0!, 16.0!)
        Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
        Me.ClientSize = New System.Drawing.Size(800, 619)
        Me.Controls.Add(Me.btn_LimparCustom)
        Me.Controls.Add(Me.Label6)
        Me.Controls.Add(Me.lbl_EstadoLigacaoPLC)
        Me.Controls.Add(Me.Label4)
        Me.Controls.Add(Me.tb_CustomMensagem)
        Me.Controls.Add(Me.Label3)
        Me.Controls.Add(Me.Label2)
        Me.Controls.Add(Me.Label1)
        Me.Controls.Add(Me.tb_ComunicacaoRasp)
        Me.Controls.Add(Me.btn_LimparLog)
        Me.Controls.Add(Me.btn_SendCustom)
        Me.Controls.Add(Me.btn_SendNOK)
        Me.Controls.Add(Me.btn_SendOK)
        Me.Controls.Add(Me.btn_ConnectPLC)
        Me.Name = "Form2"
        Me.Text = "Form2"
        Me.ResumeLayout(False)
        Me.PerformLayout()

    End Sub

    Friend WithEvents btn_ConnectPLC As Button
    Friend WithEvents btn_SendOK As Button
    Friend WithEvents btn_SendNOK As Button
    Friend WithEvents btn_SendCustom As Button
    Friend WithEvents btn_LimparLog As Button
    Friend WithEvents tb_ComunicacaoRasp As TextBox
    Friend WithEvents Label1 As Label
    Friend WithEvents Label2 As Label
    Friend WithEvents Label3 As Label
    Friend WithEvents tb_CustomMensagem As TextBox
    Friend WithEvents Label4 As Label
    Friend WithEvents lbl_EstadoLigacaoPLC As Label
    Friend WithEvents Label6 As Label
    Friend WithEvents btn_LimparCustom As Button
End Class
