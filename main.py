import sys
import sqlite3
from PyQt5.QtCore import QDate, Qt, QSize
from PyQt5.QtGui import QIcon, QFont, QColor, QPalette, QPixmap, QBrush, QLinearGradient
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QDialog, QFormLayout,
    QLineEdit, QComboBox, QDateEdit, QMessageBox, QLabel, QGroupBox, QSizePolicy,
    QHeaderView, QFrame, QScrollArea, QGridLayout, QToolButton, QStyleFactory, QSplitter
)
from database import crear_tablas, guardar_actividad, obtener_actividades, actualizar_actividad, eliminar_actividad

class AddActivityDialog(QDialog):
    def __init__(self, actividad=None):
        super().__init__()
        self.setWindowTitle("Agregar Actividad" if not actividad else "Editar Actividad")
        self.setWindowIcon(QIcon.fromTheme("task-new"))
        self.setMinimumSize(450, 350)
        self.tipo_mapping = {
            "Evaluación": "evaluacion",
            "Certificación": "certificacion",
            "Administrativa": "administrativa"
        }
        
        # ================= ESTILOS =================
        self.setStyleSheet('''
            QDialog {
                background-color: #F8F9FA;
                border: 1px solid #DEE2E6;
                border-radius: 10px;
            }
            QLabel {
                color: #343A40;
                font-weight: 500;
                font-size: 14px;
                margin-bottom: 5px;
            }
            QPushButton {
                background-color: #0078D4;
                color: white;
                border: none;
                padding: 10px 24px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #0056B3;
            }
            QPushButton:pressed {
                background-color: #004494;
            }
            QLineEdit, QComboBox, QDateEdit {
                padding: 10px;
                border: 1px solid #CED4DA;
                border-radius: 5px;
                background-color: white;
                font-size: 14px;
                selection-background-color: #0078D4;
                min-height: 20px;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
                border: 2px solid #0078D4;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                width: 14px;
                height: 14px;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 16px;
                color: #0078D4;
                margin-top: 20px;
                border: 1px solid #DEE2E6;
                border-radius: 8px;
                padding: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 10px;
                background-color: white;
            }
        ''')
        
        # ================= CONTENIDO =================
        grupo_datos = QGroupBox("Datos de la Actividad")

        # Campos del formulario
        self.titulo = QLineEdit()
        self.titulo.setPlaceholderText("Ingrese el título de la actividad")
        
        self.tipo = QComboBox()
        self.tipo.addItems(["Evaluación", "Certificación", "Administrativa"])
        
        self.estado = QComboBox()
        self.estado.addItems(["Pendiente", "En Proceso", "Completada"])
        
        self.fecha_limite = QDateEdit()
        self.fecha_limite.setCalendarPopup(True)
        self.fecha_limite.setDate(QDate.currentDate())
        
        self.responsable = QLineEdit()
        self.responsable.setPlaceholderText("Nombre del responsable")

        # Rellenar datos si es edición
        if actividad:
            reverse_tipo_mapping = {v: k for k, v in self.tipo_mapping.items()}
            tipo_db = actividad[2]
            self.tipo.setCurrentText(reverse_tipo_mapping.get(tipo_db, "Evaluación"))
            self.titulo.setText(actividad[1])
            self.tipo.setCurrentText(actividad[2].capitalize())
            self.estado.setCurrentText(actividad[3].replace("_", " ").title())
            self.fecha_limite.setDate(QDate.fromString(actividad[4], "yyyy-MM-dd"))
            self.responsable.setText(actividad[5])

        # Etiquetas con asterisco para campos obligatorios
        titulo_lbl = QLabel("Título<font color='#FF0000'>*</font>:")
        tipo_lbl = QLabel("Tipo<font color='#FF0000'>*</font>:")
        estado_lbl = QLabel("Estado<font color='#FF0000'>*</font>:")
        fecha_lbl = QLabel("Fecha Límite:")
        responsable_lbl = QLabel("Responsable:")

        # Diseño del formulario
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.setContentsMargins(15, 20, 15, 10)
        form_layout.addRow(titulo_lbl, self.titulo)
        form_layout.addRow(tipo_lbl, self.tipo)
        form_layout.addRow(estado_lbl, self.estado)
        form_layout.addRow(fecha_lbl, self.fecha_limite)
        form_layout.addRow(responsable_lbl, self.responsable)
        grupo_datos.setLayout(form_layout)

        # Nota campos obligatorios
        nota_lbl = QLabel("<font color='#FF0000'>*</font> Campos obligatorios")
        nota_lbl.setStyleSheet("color: #6C757D; font-size: 12px; font-style: italic;")

        # Botones
        btn_layout = QHBoxLayout()
        self.btn_guardar = QPushButton(QIcon.fromTheme("dialog-ok"), " Guardar")
        self.btn_guardar.setIcon(QIcon.fromTheme("dialog-ok"))
        self.btn_guardar.setIconSize(QSize(20, 20))
        self.btn_guardar.clicked.connect(self.validar_y_guardar)
        
        self.btn_cancelar = QPushButton(QIcon.fromTheme("dialog-cancel"), " Cancelar")
        self.btn_cancelar.setIcon(QIcon.fromTheme("dialog-cancel"))
        self.btn_cancelar.setIconSize(QSize(20, 20))
        self.btn_cancelar.setStyleSheet('''
            background-color: #6C757D;
            color: white;
            border: none;
            padding: 10px 24px;
            border-radius: 5px;
            font-size: 14px;
            font-weight: bold;
            min-width: 120px;
        ''')
        self.btn_cancelar.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.btn_guardar)
        btn_layout.addWidget(self.btn_cancelar)
        btn_layout.setContentsMargins(10, 10, 10, 10)

        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.addWidget(grupo_datos)
        main_layout.addWidget(nota_lbl)
        main_layout.addLayout(btn_layout)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        self.setLayout(main_layout)

    def validar_y_guardar(self):
        if not self.titulo.text().strip():
            QMessageBox.critical(self, "Error", "❌ El título es obligatorio")
            return
        if self.fecha_limite.date() < QDate.currentDate():
            QMessageBox.warning(self, "Advertencia", "⚠️ La fecha no puede ser anterior al día actual")
            return
        self.accept()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema Red CONOCER")
        self.setWindowIcon(QIcon.fromTheme("office-calendar"))
        self.setGeometry(100, 100, 1280, 720)
        
        # ================= ESTILOS GLOBALES =================
        self.setStyleSheet('''
            QMainWindow {
                background-color: #F0F2F5;
                font-family: 'Segoe UI';
            }
            QTabWidget {
                background-color: #F0F2F5;
            }
            QTableWidget {
                background-color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                selection-background-color: #E3F2FD;
                selection-color: #212529;
                gridline-color: #E9ECEF;
                alternate-background-color: #F8F9FA;
            }
            QHeaderView::section {
                background-color: #0078D4;
                color: white;
                padding: 14px;
                border: none;
                font-size: 14px;
                font-weight: bold;
            }
            QHeaderView::section:first {
                border-top-left-radius: 8px;
            }
            QHeaderView::section:last {
                border-top-right-radius: 8px;
            }
            QPushButton {
                background-color: #0078D4;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #0056B3;
            }
            QPushButton:pressed {
                background-color: #004494;
            }
            QComboBox, QLineEdit, QDateEdit {
                padding: 10px;
                border: 1px solid #CED4DA;
                border-radius: 6px;
                background-color: white;
                font-size: 14px;
                min-height: 20px;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                width: 14px;
                height: 14px;
            }
            QLabel {
                font-size: 14px;
                color: #495057;
                font-weight: 500;
            }
            QTabWidget::pane {
                border: none;
                background-color: #F0F2F5;
            }
            QTabBar::tab {
                background: #E9ECEF;
                color: #495057;
                padding: 14px 28px;
                border: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 4px;
                font-weight: bold;
                font-size: 14px;
            }
            QTabBar::tab:selected {
                background: #0078D4;
                color: white;
            }
            QScrollBar:vertical {
                border: none;
                background: #F8F9FA;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #ADB5BD;
                min-height: 30px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background: #6C757D;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QMessageBox {
                background-color: #FFFFFF;
            }
            QMessageBox QPushButton {
                min-width: 100px;
                min-height: 30px;
            }
        ''')

        # ================= COMPONENTES PRINCIPALES =================
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Pestaña de actividades
        self.tab_actividades = QWidget()
        self.tabs.addTab(self.tab_actividades, " Gestión de Actividades")
        
        # Encabezado con logo y título
        header_layout = QHBoxLayout()
        
        logo_label = QLabel()
        # Si tienes un logo, puedes descomentar estas líneas
        # logo = QPixmap("path/to/logo.png")
        # logo_label.setPixmap(logo.scaled(120, 60, Qt.KeepAspectRatio))
        logo_label.setText("RED CONOCER")
        logo_label.setStyleSheet('''
            font-size: 24px;
            font-weight: bold;
            color: #0078D4;
            padding: 10px;
        ''')
        
        titulo_sistema = QLabel("Sistema de Gestión de Actividades")
        titulo_sistema.setStyleSheet('''
            font-size: 20px;
            font-weight: normal;
            color: #495057;
            padding: 10px;
        ''')
        
        header_layout.addWidget(logo_label)
        header_layout.addWidget(titulo_sistema)
        header_layout.addStretch()
        
        # Fecha actual
        fecha_actual = QLabel(f"Fecha: {QDate.currentDate().toString('dddd, dd MMMM yyyy')}")
        fecha_actual.setStyleSheet('''
            font-size: 14px;
            color: #6C757D;
            padding: 10px;
        ''')
        header_layout.addWidget(fecha_actual)

        # ================= PANEL DE FILTROS =================
        filtros_frame = QFrame()
        filtros_frame.setFrameShape(QFrame.StyledPanel)
        filtros_frame.setStyleSheet('''
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #DEE2E6;
            }
        ''')
        
        filtros_layout = QHBoxLayout(filtros_frame)
        filtros_layout.setContentsMargins(20, 15, 20, 15)
        
        filtro_tipo_lbl = QLabel("Filtrar por tipo:")
        self.filtro_tipo = QComboBox()
        self.filtro_tipo.addItems(["Todos", "Evaluación", "Certificación", "Administrativa"])
        self.filtro_tipo.setCurrentIndex(0)
        self.filtro_tipo.setFixedWidth(200)
        self.filtro_tipo.currentIndexChanged.connect(self.aplicar_filtros)

        filtro_estado_lbl = QLabel("Filtrar por estado:")
        self.filtro_estado = QComboBox()
        self.filtro_estado.addItems(["Todos", "Pendiente", "En Proceso", "Completada"])
        self.filtro_estado.setCurrentIndex(0)
        self.filtro_estado.setFixedWidth(200)
        self.filtro_estado.currentIndexChanged.connect(self.aplicar_filtros)

        filtros_layout.addWidget(filtro_tipo_lbl)
        filtros_layout.addWidget(self.filtro_tipo)
        filtros_layout.addSpacing(20)
        filtros_layout.addWidget(filtro_estado_lbl)
        filtros_layout.addWidget(self.filtro_estado)
        filtros_layout.addStretch()
        
        # Botón para limpiar filtros
        btn_limpiar = QPushButton(QIcon.fromTheme("edit-clear"), " Limpiar Filtros")
        btn_limpiar.setIconSize(QSize(16, 16))
        btn_limpiar.setFixedWidth(150)
        btn_limpiar.setStyleSheet('''
            background-color: #6C757D;
            padding: 8px 16px;
            min-width: 120px;
        ''')
        btn_limpiar.clicked.connect(self.limpiar_filtros)
        filtros_layout.addWidget(btn_limpiar)

        # ================= TABLA DE ACTIVIDADES =================
        tabla_frame = QFrame()
        tabla_frame.setFrameShape(QFrame.StyledPanel)
        tabla_frame.setStyleSheet('''
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #DEE2E6;
            }
        ''')
        
        tabla_layout = QVBoxLayout(tabla_frame)
        tabla_layout.setContentsMargins(15, 15, 15, 15)

        # Título de la sección
        seccion_titulo = QLabel("Listado de Actividades")
        seccion_titulo.setStyleSheet('''
            font-size: 18px;
            font-weight: bold;
            color: #212529;
            margin-bottom: 10px;
        ''')
        tabla_layout.addWidget(seccion_titulo)
        
        # Tabla
        self.tabla_actividades = QTableWidget()
        self.tabla_actividades.setColumnCount(8)
        self.tabla_actividades.setHorizontalHeaderLabels(
            ["ID", "Título", "Tipo", "Estado", "Fecha Límite", "Responsable", "", ""]
        )
        self.tabla_actividades.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.tabla_actividades.verticalHeader().setVisible(False)
        self.tabla_actividades.setAlternatingRowColors(True)
        self.tabla_actividades.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tabla_actividades.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla_actividades.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_actividades.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tabla_actividades.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
        self.tabla_actividades.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeToContents)
        tabla_layout.addWidget(self.tabla_actividades)

        # ================= BOTONES PRINCIPALES =================
        btn_frame = QFrame()
        btn_frame.setStyleSheet('''
            QFrame {
                background-color: transparent;
            }
        ''')
        btn_layout = QHBoxLayout(btn_frame)
        btn_layout.setContentsMargins(0, 10, 0, 0)
        
        self.btn_agregar = QPushButton(QIcon.fromTheme("list-add"), " Nueva Actividad")
        self.btn_agregar.setIcon(QIcon.fromTheme("list-add"))
        self.btn_agregar.setIconSize(QSize(24, 24))
        self.btn_agregar.clicked.connect(self.abrir_formulario)
        
        self.btn_exportar_excel = QPushButton(QIcon.fromTheme("x-office-spreadsheet"), " Exportar a Excel")
        self.btn_exportar_excel.setIcon(QIcon.fromTheme("x-office-spreadsheet"))
        self.btn_exportar_excel.setIconSize(QSize(24, 24))
        self.btn_exportar_excel.clicked.connect(self.exportar_excel)
        
        self.btn_exportar_pdf = QPushButton(QIcon.fromTheme("application-pdf"), " Exportar a PDF")
        self.btn_exportar_pdf.setIcon(QIcon.fromTheme("application-pdf"))
        self.btn_exportar_pdf.setIconSize(QSize(24, 24))
        self.btn_exportar_pdf.clicked.connect(self.exportar_pdf)
        
        # Aplicar estilo verde al botón de añadir
        self.btn_agregar.setStyleSheet('''
            background-color: #28A745;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            font-size: 14px;
            font-weight: bold;
            min-width: 180px;
        ''')
        self.btn_agregar.setStyleSheet('''
            background-color: #28A745;
        ''')
        self.btn_agregar.setStyleSheet('''
            background-color: #28A745;
        ''')
        
        btn_layout.addWidget(self.btn_agregar)
        btn_layout.addWidget(self.btn_exportar_excel)
        btn_layout.addWidget(self.btn_exportar_pdf)
        btn_layout.addStretch()

        # ================= LAYOUT FINAL =================
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        main_layout.addLayout(header_layout)
        main_layout.addWidget(filtros_frame)
        main_layout.addWidget(tabla_frame)
        main_layout.addWidget(btn_frame)
        self.tab_actividades.setLayout(main_layout)

        # Cargar datos iniciales
        self.aplicar_filtros()

    # ================= MÉTODOS PRINCIPALES =================
    def limpiar_filtros(self):
        self.filtro_tipo.setCurrentIndex(0)
        self.filtro_estado.setCurrentIndex(0)
        self.aplicar_filtros()
    
    def abrir_formulario(self):
        dialog = AddActivityDialog()
        if dialog.exec_() == QDialog.Accepted:
            datos = {
                "titulo": dialog.titulo.text().strip(),
                "tipo": dialog.tipo_mapping[dialog.tipo.currentText()],  # Línea modificada
                "estado": dialog.estado.currentText().lower().replace(" ", "_"),
                "fecha": dialog.fecha_limite.date().toString("yyyy-MM-dd"),
                "responsable": dialog.responsable.text().strip()
            }
            guardar_actividad(datos)
            self.aplicar_filtros()
            
            # Mostrar mensaje de éxito
            QMessageBox.information(
                self, 
                "Éxito", 
                "✅ Actividad guardada correctamente",
                QMessageBox.Ok
            )

    def aplicar_filtros(self):
        tipo = self.filtro_tipo.currentText().lower() if self.filtro_tipo.currentText() != "Todos" else "Todos"
        estado = self.filtro_estado.currentText().lower().replace(" ", "_") if self.filtro_estado.currentText() != "Todos" else "Todos"
        actividades = obtener_actividades(tipo, estado)
        self.mostrar_actividades(actividades)

    def mostrar_actividades(self, actividades):
        self.tabla_actividades.setRowCount(0)
        for row_idx, row_data in enumerate(actividades):
            self.tabla_actividades.insertRow(row_idx)
            
            # Formatear datos para visualización
            tipo_formateado = row_data[2].capitalize()
            estado_formateado = row_data[3].replace("_", " ").title()
            fecha_formateada = QDate.fromString(row_data[4], "yyyy-MM-dd").toString("dd/MM/yyyy")

            # Llenar celdas
            items = [
                str(row_data[0]), 
                row_data[1], 
                tipo_formateado,
                estado_formateado,
                fecha_formateada,
                row_data[5]
            ]
            
            for col_idx, col_data in enumerate(items):
                item = QTableWidgetItem(col_data)
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)  # Hacer celdas no editables
                
                # Aplicar color de fondo según el estado
                if col_idx == 3:  # Columna de estado
                    if estado_formateado == "Pendiente":
                        item.setBackground(QColor("#FFF3CD"))
                        item.setForeground(QColor("#856404"))
                    elif estado_formateado == "En Proceso":
                        item.setBackground(QColor("#CCE5FF"))
                        item.setForeground(QColor("#004085"))
                    elif estado_formateado == "Completada":
                        item.setBackground(QColor("#D4EDDA"))
                        item.setForeground(QColor("#155724"))
                
                self.tabla_actividades.setItem(row_idx, col_idx, item)

            # Botones de acciones
            btn_editar = QPushButton(QIcon.fromTheme("document-edit"), " Editar")
            btn_editar.setToolTip("Editar")
            btn_editar.setStyleSheet('''
                QPushButton {
                    background-color: #17A2B8;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 5px;
                    icon-size: 20px;
                }
                QPushButton:hover {
                    background-color: #138496;
                }
            ''')
            btn_editar.clicked.connect(lambda _, r=row_data: self.editar_actividad(r))
            
            btn_eliminar = QPushButton(QIcon.fromTheme("edit-delete"), " Eliminar")
            btn_eliminar.setToolTip("Eliminar")
            btn_eliminar.setStyleSheet('''
                QPushButton {
                    background-color: #DC3545;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 5px;
                    icon-size: 20px;
                }
                QPushButton:hover {
                    background-color: #C82333;
                }
            ''')
            btn_eliminar.clicked.connect(lambda _, r=row_data: self.eliminar_actividad(r[0]))

            # Añadir botones a la tabla
            self.tabla_actividades.setCellWidget(row_idx, 6, btn_editar)
            self.tabla_actividades.setCellWidget(row_idx, 7, btn_eliminar)

        # Ajustar tamaño de columnas
        self.tabla_actividades.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabla_actividades.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tabla_actividades.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
        self.tabla_actividades.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeToContents)

    def editar_actividad(self, actividad):
        dialog = AddActivityDialog(actividad)
        if dialog.exec_() == QDialog.Accepted:
            nuevos_datos = {
                "id": actividad[0],
                "titulo": dialog.titulo.text().strip(),
                "tipo": dialog.tipo_mapping[dialog.tipo.currentText()],
                "estado": dialog.estado.currentText().lower().replace(" ", "_"),
                "fecha": dialog.fecha_limite.date().toString("yyyy-MM-dd"),
                "responsable": dialog.responsable.text().strip()
            }
            actualizar_actividad(nuevos_datos)
            self.aplicar_filtros()
            
            # Mostrar mensaje de éxito
            QMessageBox.information(
                self, 
                "Éxito", 
                "✅ Actividad actualizada correctamente",
                QMessageBox.Ok
            )

    def eliminar_actividad(self, id_actividad):
        confirmar = QMessageBox.question(
            self, 
            "Eliminar", 
            "¿Estás seguro de que deseas eliminar esta actividad?\nEsta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if confirmar == QMessageBox.Yes:
            eliminar_actividad(id_actividad)
            self.aplicar_filtros()
            
            # Mostrar mensaje de éxito
            QMessageBox.information(
                self, 
                "Éxito", 
                "✅ Actividad eliminada correctamente",
                QMessageBox.Ok
            )

    def exportar_excel(self):
        from reportes import exportar_excel
        exportar_excel()
        QMessageBox.information(
            self, 
            "Exportación Exitosa", 
            "✅ El reporte Excel ha sido generado correctamente.\n\nArchivo: actividades.xlsx",
            QMessageBox.Ok
        )

    def exportar_pdf(self):
        from reportes import exportar_pdf
        exportar_pdf()
        QMessageBox.information(
            self, 
            "Exportación Exitosa", 
            "✅ El reporte PDF ha sido generado correctamente.\n\nArchivo: reporte.pdf",
            QMessageBox.Ok
        )

if __name__ == "__main__":
    crear_tablas()
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Fusion"))  # Usar estilo Fusion para una apariencia más moderna
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())