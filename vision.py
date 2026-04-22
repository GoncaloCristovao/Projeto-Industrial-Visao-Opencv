import cv2
import os
import numpy as np


class VisionProcessor:
    def __init__(self):
        self.caminho_padrao = "guia_luz_padrao.jpg"

        if os.path.exists(self.caminho_padrao):
            self.imagem_padrao = cv2.imread(self.caminho_padrao)
            print("[Visão] Padrão existente carregado do disco.")
        else:
            self.imagem_padrao = None
            print("[Visão] Aviso: Nenhum padrão guardado no disco. Precisa de configurar um!")

        # Parâmetros ajustáveis
        self.scale = 0.7
        self.threshold_value = 230
        self.half_thickness = 18
        self.num_parts = 10

    def set_parameters(self, params):
        """
        Atualiza parâmetros recebidos do servidor.
        """
        if not isinstance(params, dict):
            return

        self.threshold_value = params.get("threshold_value", self.threshold_value)
        self.half_thickness = params.get("half_thickness", self.half_thickness)
        self.num_parts = params.get("num_parts", self.num_parts)

    def save_new_standard(self, frame):
        """
        Guarda uma nova imagem padrão.
        """
        if frame is not None:
            try:
                sucesso = cv2.imwrite(self.caminho_padrao, frame)

                if sucesso:
                    self.imagem_padrao = frame.copy()
                    print(f"[Visão] NOVO PADRÃO INDUSTRIAL GUARDADO: {self.caminho_padrao}")
                else:
                    print("[Visão] Erro técnico ao gravar o ficheiro JPG no disco.")

            except Exception as e:
                print(f"[Visão] Erro ao guardar novo padrão: {e}")

    def _resize_to_width(self, img, width=400):
        h, w = img.shape[:2]
        scale = width / w
        new_h = int(h * scale)
        return cv2.resize(img, (width, new_h))

    def _add_label(self, img, text):
        out = img.copy()
        cv2.putText(out, text, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                    (0, 255, 0), 2)
        return out

    def _force_height(self, im, h):
        return cv2.resize(im, (im.shape[1], h))

    def process_and_decide(self, frame):
        """
        Recebe um frame da câmara, processa a guia de luz e devolve:
        - is_ok: bool
        - frame_proc: imagem processada
        - dados: dicionário com métricas
        """
        if frame is None:
            return False, None, {"erro": "Frame inválido"}

        try:
            # Preparação
            img = frame.copy()

            if self.scale != 1.0:
                img = cv2.resize(img, None, fx=self.scale, fy=self.scale)

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5, 5), 0)

            # Threshold
            _, thresh = cv2.threshold(
                blur,
                self.threshold_value,
                255,
                cv2.THRESH_BINARY
            )

            # Limpeza
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

            # Deteção de linha
            lines = cv2.HoughLinesP(
                thresh,
                1,
                np.pi / 180,
                threshold=80,
                minLineLength=200,
                maxLineGap=30
            )

            if lines is None:
                debug = img.copy()
                cv2.putText(debug, "FALHA: linha nao encontrada", (20, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                return False, debug, {
                    "erro": "Nenhuma linha encontrada",
                    "zonas": []
                }

            # Escolher a linha mais comprida
            best_line = None
            best_length = 0

            for line in lines:
                x1, y1, x2, y2 = line[0]
                length = np.hypot(x2 - x1, y2 - y1)
                if length > best_length:
                    best_length = length
                    best_line = (x1, y1, x2, y2)

            x1, y1, x2, y2 = best_line

            line_img = img.copy()
            cv2.line(line_img, (x1, y1), (x2, y2), (0, 0, 255), 3)

            # Retângulo alinhado
            dx = x2 - x1
            dy = y2 - y1
            length = np.hypot(dx, dy)

            if length == 0:
                return False, img, {"erro": "Comprimento da linha é zero", "zonas": []}

            ux = dx / length
            uy = dy / length

            px = -uy
            py = ux

            half_thickness = self.half_thickness

            p1 = (int(x1 + px * half_thickness), int(y1 + py * half_thickness))
            p2 = (int(x2 + px * half_thickness), int(y2 + py * half_thickness))
            p3 = (int(x2 - px * half_thickness), int(y2 - py * half_thickness))
            p4 = (int(x1 - px * half_thickness), int(y1 - py * half_thickness))

            box = np.array([p1, p2, p3, p4], dtype=np.int32)

            # Máscara e segmentação
            mask = np.zeros_like(gray)
            cv2.fillConvexPoly(mask, box, 255)

            segmented = cv2.bitwise_and(img, img, mask=mask)

            result = img.copy()
            cv2.polylines(result, [box], True, (0, 255, 0), 3)

            # Divisão em zonas
            divided_img = segmented.copy()
            num_parts = self.num_parts
            zonas_info = []

            for i in range(1, num_parts):
                t = i / num_parts

                top_x = int((1 - t) * p1[0] + t * p2[0])
                top_y = int((1 - t) * p1[1] + t * p2[1])

                bot_x = int((1 - t) * p4[0] + t * p3[0])
                bot_y = int((1 - t) * p4[1] + t * p3[1])

                cv2.line(divided_img, (top_x, top_y), (bot_x, bot_y), (255, 0, 0), 2)

            for i in range(num_parts):
                t = (i + 0.5) / num_parts

                top_x = (1 - t) * p1[0] + t * p2[0]
                top_y = (1 - t) * p1[1] + t * p2[1]

                bot_x = (1 - t) * p4[0] + t * p3[0]
                bot_y = (1 - t) * p4[1] + t * p3[1]

                cx = int((top_x + bot_x) / 2)
                cy = int((top_y + bot_y) / 2)

                cv2.putText(divided_img, str(i + 1), (cx - 10, cy + 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

            # Extração e análise das zonas
            zones = []

            for i in range(num_parts):
                t1 = i / num_parts
                t2 = (i + 1) / num_parts

                top1 = (
                    int((1 - t1) * p1[0] + t1 * p2[0]),
                    int((1 - t1) * p1[1] + t1 * p2[1])
                )
                top2 = (
                    int((1 - t2) * p1[0] + t2 * p2[0]),
                    int((1 - t2) * p1[1] + t2 * p2[1])
                )
                bot2 = (
                    int((1 - t2) * p4[0] + t2 * p3[0]),
                    int((1 - t2) * p4[1] + t2 * p3[1])
                )
                bot1 = (
                    int((1 - t1) * p4[0] + t1 * p3[0]),
                    int((1 - t1) * p4[1] + t1 * p3[1])
                )

                zone_poly = np.array([top1, top2, bot2, bot1], dtype=np.int32)

                zone_mask = np.zeros_like(gray)
                cv2.fillConvexPoly(zone_mask, zone_poly, 255)

                zone_img = cv2.bitwise_and(img, img, mask=zone_mask)

                x, y, w, h = cv2.boundingRect(zone_poly)
                crop = zone_img[y:y+h, x:x+w]

                if crop.size == 0:
                    brilho_medio = 0.0
                else:
                    zona_gray = gray[zone_mask == 255]
                    brilho_medio = float(np.mean(zona_gray)) if zona_gray.size > 0 else 0.0

                zones.append(crop)
                zonas_info.append({
                    "zona": i + 1,
                    "brilho_medio": round(brilho_medio, 2)
                })

            # Critério simples OK/NOK
            brilhos = [z["brilho_medio"] for z in zonas_info if z["brilho_medio"] > 0]

            if len(brilhos) == 0:
                is_ok = False
            else:
                brilho_medio_global = float(np.mean(brilhos))
                brilho_min = float(min(brilhos))

                # Critério inicial simples:
                # se alguma zona estiver muito abaixo da média => NOK
                is_ok = brilho_min >= 0.7 * brilho_medio_global

            # Frame final para HMI/debug
            thresh_bgr = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
            mask_bgr = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

            img_r = self._resize_to_width(img, 400)
            thresh_r = self._resize_to_width(thresh_bgr, 400)
            line_r = self._resize_to_width(line_img, 400)
            result_r = self._resize_to_width(result, 400)
            mask_r = self._resize_to_width(mask_bgr, 400)
            seg_r = self._resize_to_width(segmented, 400)
            div_r = self._resize_to_width(divided_img, 400)

            target_h = min(
                img_r.shape[0], thresh_r.shape[0], line_r.shape[0], result_r.shape[0],
                mask_r.shape[0], seg_r.shape[0], div_r.shape[0]
            )

            img_r = self._force_height(img_r, target_h)
            thresh_r = self._force_height(thresh_r, target_h)
            line_r = self._force_height(line_r, target_h)
            result_r = self._force_height(result_r, target_h)
            mask_r = self._force_height(mask_r, target_h)
            seg_r = self._force_height(seg_r, target_h)
            div_r = self._force_height(div_r, target_h)

            img_r = self._add_label(img_r, "Original")
            thresh_r = self._add_label(thresh_r, "Threshold")
            line_r = self._add_label(line_r, "Linha")
            result_r = self._add_label(result_r, "Retangulo")
            mask_r = self._add_label(mask_r, "Mascara")
            seg_r = self._add_label(seg_r, "Segmentada")
            div_r = self._add_label(div_r, "Divisao em zonas")

            status_panel = np.zeros_like(div_r)
            status_text = "OK" if is_ok else "NOK"
            status_color = (0, 255, 0) if is_ok else (0, 0, 255)

            cv2.putText(status_panel, f"RESULTADO: {status_text}", (20, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, status_color, 3)

            y_text = 110
            for z in zonas_info[:5]:
                cv2.putText(status_panel,
                            f"Z{z['zona']}: {z['brilho_medio']:.1f}",
                            (20, y_text),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                y_text += 35

            top = np.hstack([img_r, thresh_r, line_r, result_r])
            bottom = np.hstack([mask_r, seg_r, div_r, status_panel])
            frame_proc = np.vstack([top, bottom])

            dados = {
                "is_ok": is_ok,
                "num_zonas": num_parts,
                "linha_detetada": [x1, y1, x2, y2],
                "zonas": zonas_info
            }

            return is_ok, frame_proc, dados

        except Exception as e:
            erro_img = frame.copy()
            cv2.putText(erro_img, f"Erro: {str(e)}", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

            return False, erro_img, {"erro": str(e)}