
"""
Práctica cuatro: Modelado y control del sistema endócrino

Departamento de Ingeniería Eléctrica y Electrónica, Ingeniería Biomédica
Tecnológico Nacional de México [TecNM - Tijuana]
Blvd. Alberto Limón Padilla s/n, C.P. 22454, Tijuana, B.C., México

Nombre del alumno: Carolina Gamez Flores
Número de control: 23212193
Correo institucional: l23212193@tectijuana.edu.mx

Asignatura: Modelado de Sistemas Fisiológicos
Docente: Dr. Paul Antonio Valle Trujillo; paul.valle@tectijuana.edu.mx
"""

import numpy as np
import math as m
import matplotlib.pyplot as plt
from scipy import signal
import control as ctrl
import pandas as pd

# Datos de la simulación
x0,t0,tend,dt,w,h = 0,0,5,1E-3,10,5
N = round((tend-t0)/dt)+1
t = np.linspace(t0,tend,N)
u = np.ones(N)

# Componentes del circuito RLC
def endocrino(C,R2):
    R1,L = 1E3,100E-3
    num = [L,R2]
    den = [R1*L*C,L+R1*R2*C,R1+R2]
    sys = ctrl.tf(num,den)
    polos = np.roots(den)
    return sys,polos

# Función de transferencia de control
C,R2 = 1E-6,100E3
sysControl,L = endocrino(C,R2)
print(f"Función de transferencia del control: {sysControl}")
print(f"Polos del sistema: L1 = {L[0]:.3e}, L2 = {L[1]:.3e}\n")

# Función de transferencia de caso
C,R2 = 1000E-6,1E3
sysCaso,L = endocrino(C,R2)
print(f"Función de transferencia del caso: {sysCaso}")
print(f"Polos del sistema: L1 = {L[0]:.3e}, L2 = {L[1]:.3e}\n")

# Respuesta del sistema en lazo abierto
_,VsControl = ctrl.forced_response(sysControl,t,u,x0)
_,VsCaso = ctrl.forced_response(sysCaso,t,u,x0)

# Error en estado estacionario
essControl = 1-ctrl.dcgain(sysControl)
essCaso = 1-ctrl.dcgain(sysCaso)
print(f"Error estacionario del control: {essControl:.6f}")
print(f"Error estacionario del caso: {essCaso:.6f}")
print(f"Diferencia final entre control y caso: {essCaso-essControl:.6f}\n")

# Parámetros del controlador PID
kP = 962.368141439034
kI = 171510.840008335
kD = 0.179170949090154
Nf = 3678.01770617189

# Componentes del controlador analógico ideal
Cr = 1E-6
Re = 1/(Cr*kI)
Rr = kP*Re
Ce = kD/Rr

print(f"Capacitancia Cr = {Cr:.9e} F")
print(f"Resistencia Re = {Re:.9f} Ohms")
print(f"Resistencia Rr = {Rr:.9f} Ohms")
print(f"Capacitancia Ce = {Ce:.9e} F")


# Función de transferencia del controlador PID filtrado
# PID(s) = kP + kI/s + kD*Nf*s/(s+Nf)
numPID = [kP+kD*Nf,kP*Nf+kI,kI*Nf]
denPID = [1,Nf,0]
PID = ctrl.tf(numPID,denPID)

print(f"Función de transferencia del controlador PID: {PID}\n")

# Sistema de control en lazo cerrado
sysPID = ctrl.feedback(ctrl.series(PID,sysCaso),1,sign=-1)
print(f"Función de transferencia del sistema endócrino en lazo cerrado: {sysPID}\n")

# Polos del sistema con PID
polosPID = ctrl.poles(sysPID)
print(f"Polos del sistema con PID: {polosPID}\n")

# Respuesta del sistema en lazo cerrado
# La respuesta del control se utiliza como referencia
_,VsPID = ctrl.forced_response(sysPID,t,VsControl,x0)

# Error de seguimiento
error = VsControl-VsPID
print(f"Error final de seguimiento simulado: {error[-1]:.9f}")
print(f"Ganancia DC del sistema con PID: {ctrl.dcgain(sysPID):.9f}\n")

# Colores
clr1 = np.array([246,36,119])/255
clr2 = np.array([255,173,238])/255
clr3 = np.array([146,0,58])/255
clr4 = np.array([128,81,255])/255

# Gráfica
fg = plt.figure(1)
fg.set_size_inches(w,h)
plt.rcParams['font.size'] = 11
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = 'Times New Roman'

plt.plot(t,u,'-',linewidth=0.7,color=clr1,label='Ve(t): Entrada')
plt.plot(t,VsControl,'-',linewidth=1,color=clr2,label='Vs(t): Control')
plt.plot(t,VsCaso,'-',linewidth=1,color=clr3,label='Vs(t): Caso')
plt.plot(t,VsPID,':',linewidth=1.5,color=clr4,label='Vs(t): Caso PID')

plt.xlim(0,5); plt.xticks(np.arange(0,5.1,0.5))
plt.ylim(-0.1,1.1); plt.yticks(np.arange(-0.1,1.11,0.1))
plt.xlabel('t [s]')
plt.ylabel('Vs(t) [V]')
plt.legend(bbox_to_anchor=(0.5,-0.25),loc='center',ncol=4,frameon=False)
plt.grid(True,alpha=0.2)
fg.savefig('caso_python.pdf',bbox_inches='tight')
plt.show()
