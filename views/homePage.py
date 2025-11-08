import ttkbootstrap as ttk
from ttkbootstrap.widgets import DateEntry, Combobox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, time
import pandas as pd
import numpy as np
import tkinter.messagebox as mb
from services.api import getLecturas

class HomePage(ttk.Frame):
    def __init__(self,parent):
        super().__init__(parent,padding=10)
        self.pack(fill="both",expand=True)
        sidebar=ttk.Frame(self,width=200)
        sidebar.pack(side="left",fill="y",padx=(0,10))
        self.mainArea=ttk.Frame(self)
        self.mainArea.pack(side="right",fill="both",expand=True)

        ttk.Label(sidebar,text="Fecha").pack(pady=(20,5))
        self.fecha=DateEntry(sidebar,bootstyle="info",dateformat="%Y-%m-%d")
        self.fecha.pack(fill="x",padx=10)

        ttk.Label(sidebar,text="Estación").pack(pady=(20,5))
        self.estacionSelect=Combobox(sidebar,values=[],bootstyle="info")
        self.estacionSelect.pack(fill="x",padx=10)

        ttk.Label(sidebar,text="Rango de hora").pack(pady=(20,5))
        self.horaSelect=Combobox(sidebar,values=["00:00-06:00","06:00-12:00","12:00-18:00","18:00-23:59","Todo el día"],bootstyle="info")
        self.horaSelect.current(4)
        self.horaSelect.pack(fill="x",padx=10)

        self.btnFiltrar=ttk.Button(sidebar,text="Filtrar",bootstyle="primary",command=self.filtrarDatos)
        self.btnFiltrar.pack(pady=(20,5),padx=10,fill="x")
        self.btnGraficas=ttk.Button(sidebar,text="Ver Gráficas",bootstyle="secondary",command=self.mostrarGraficas)
        self.btnGraficas.pack(pady=(5,5),padx=10,fill="x")
        self.btnGuardar=ttk.Button(sidebar,text="Guardar Excel",bootstyle="success",command=self.guardarExcel)
        self.btnGuardar.pack(pady=(5,20),padx=10,fill="x")

        self.df = pd.DataFrame()
        self.cargarDatos()
        self.mostrarTabla()

    def cargarDatos(self):
        data=getLecturas(limit=1000) or []
        if data:
            self.df=pd.DataFrame(data)
            self.df['timestamp']=pd.to_datetime(self.df['timestamp'],format='%Y-%m-%dT%H:%M:%S')
            self.df['unidadMedicion']=self.df['unidadMedicion'].str.strip()
        estaciones=self.df['estacionNombre'].dropna().unique() if not self.df.empty else []
        estaciones=list(sorted(estaciones))
        estaciones.insert(0,"Todas las estaciones")
        self.estacionSelect.configure(values=estaciones)

    def filtrarDatos(self):
        dfFiltrado=self.obtenerFiltro()
        for w in self.mainArea.winfo_children():
            w.destroy()
        if dfFiltrado.empty:
            lbl=ttk.Label(self.mainArea,text="No hay datos para mostrar")
            lbl.pack(expand=True)
            return
        tree=ttk.Treeview(self.mainArea,columns=list(dfFiltrado.columns),show="headings")
        for col in dfFiltrado.columns:
            tree.heading(col,text=col)
            tree.column(col,width=100,anchor="center")
        for _,row in dfFiltrado.iterrows():
            tree.insert("", "end", values=list(row))
        tree.pack(fill="both",expand=True)

    def obtenerFiltro(self):
        df=self.df.copy()
        if df.empty:
            return df
        fechaSel=pd.to_datetime(self.fecha.entry.get()).date()
        estacion=self.estacionSelect.get()
        rango=self.horaSelect.get()
        ahora=pd.Timestamp.now()
        if rango=="Todo el día":
            inicio,fin=time(0,0),time(23,59)
        else:
            inicioStr,finStr=rango.split("-")
            inicio=datetime.strptime(inicioStr,"%H:%M").time()
            fin=datetime.strptime(finStr,"%H:%M").time()
        df=df[df['timestamp'].dt.date==fechaSel]
        df=df[(df['timestamp'].dt.time>=inicio)&(df['timestamp'].dt.time<=fin)]
        df=df[df['timestamp']<=ahora]
        if estacion and estacion!="Todas las estaciones":
            df=df[df['estacionNombre']==estacion]
        return df.sort_values('timestamp')

    def mostrarTabla(self):
        for w in self.mainArea.winfo_children():
            w.destroy()
        df=self.df.sort_values('lecturaId')
        tree=ttk.Treeview(self.mainArea,columns=list(df.columns),show="headings")
        for col in df.columns:
            tree.heading(col,text=col)
            tree.column(col,width=100,anchor="center")
        for _,row in df.iterrows():
            tree.insert("", "end", values=list(row))
        tree.pack(fill="both",expand=True)

    def mostrarGraficas(self):
        dfFiltrado=self.obtenerFiltro()
        modal=ttk.Toplevel(self)
        modal.title("Gráficas")
        modal.geometry("1400x900")
        modal.resizable(False,False)
        if dfFiltrado.empty:
            lbl=ttk.Label(modal,text="No hay datos para mostrar")
            lbl.pack(expand=True)
            return

        unidades=dfFiltrado['unidadMedicion'].unique()
        frames={}
        pos=[(0,0),(0,1),(1,0),(1,1)]
        for idx,unidad in enumerate(unidades):
            if idx>3:
                break
            datos=dfFiltrado[dfFiltrado['unidadMedicion']==unidad]
            frame=ttk.Frame(modal,width=400,height=250)
            frame.grid_propagate(False)
            frame.grid(row=pos[idx][0],column=pos[idx][1],padx=10,pady=10)
            frames[unidad]=frame
            fig,ax=plt.subplots(figsize=(6,3),dpi=90)
            canvas=FigureCanvasTkAgg(fig,master=frame)
            canvas.get_tk_widget().pack(fill="both",expand=True)
            ax.clear()
            if datos.empty:
                ax.text(0.5,0.5,"No hay datos",ha="center",va="center")
                ax.axis('off')
            else:
                estaciones=datos['estacionNombre'].dropna().unique()
                colores=['tab:blue','tab:orange','tab:green','tab:red','tab:purple']
                for i,est in enumerate(estaciones):
                    datosEst=datos[datos['estacionNombre']==est]
                    times=datosEst['timestamp']
                    values=datosEst['valor']
                    if times.empty:
                        times=pd.date_range(start=pd.Timestamp.now(),periods=10,freq='H')
                        values=np.sin(np.linspace(0,2*np.pi,len(times)))*10+50
                    ax.plot(times,values,marker='o',markersize=3,linestyle='-',color=colores[i%len(colores)],label=est)
                ax.set_title(unidad,fontsize=12,fontweight='bold')
                if self.horaSelect.get()=="Todo el día":
                    locator=mdates.HourLocator(interval=4)
                else:
                    locator=mdates.HourLocator(interval=1)
                ax.xaxis.set_major_locator(locator)
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                fig.autofmt_xdate()
                ax.set_facecolor('white')
                ax.grid(True,linestyle='--',alpha=0.5)
                ax.legend(fontsize=7)
            canvas.draw()

    def guardarExcel(self):
        dfFiltrado=self.obtenerFiltro()
        if dfFiltrado.empty:
            mb.showwarning("Advertencia", "No hay datos para guardar")
            return
        try:
            archivo=f"RecoleccionDatos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            dfFiltrado.to_excel(archivo,index=False)
            mb.showinfo("Éxito",f"Datos guardados correctamente en:\n{archivo}")
        except Exception as e:
            mb.showerror("Error",f"No se pudo guardar el archivo:\n{str(e)}")