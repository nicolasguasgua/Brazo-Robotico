#include <Servo.h>

// Definición de los 6 servomotores
Servo servo1;
Servo servo2;
Servo servo3;
Servo servo4;
Servo servo5;
Servo servo6;

// Ángulos iniciales (posiciones de inicio)
int angulo1 = 45;
int angulo2 = 25;
int angulo3 = 54;
int angulo4 = 3;
int angulo5 = 160;
int angulo6 = 41;

int salto = 3; // Grados que se incrementan por lectura

// Pines analógicos para los 3 joysticks (Ejes X e Y)
const int Eje_X1 = A0;
const int Eje_Y1 = A1;
const int Eje_X2 = A2;
const int Eje_Y2 = A3;
const int Eje_X3 = A4;
const int Eje_Y3 = A5;

void setup() {
  Serial.begin(9600);
  
  // Asignación de pines PWM a cada servo
  servo1.attach(3);
  servo2.attach(5);
  servo3.attach(6);
  servo4.attach(9);
  servo5.attach(10);
  servo6.attach(11);

  // Posicionar servos en su ángulo inicial
  servo1.write(angulo1);
  servo2.write(angulo2);
  servo3.write(angulo3);
  servo4.write(angulo4);
  servo5.write(angulo5);
  servo6.write(angulo6);

  delay(100);
}

void loop() {
  // Lectura de los potenciómetros de los joysticks en Wokwi
  int x1 = analogRead(Eje_X1);
  int y1 = analogRead(Eje_Y1);
  int x2 = analogRead(Eje_X2);
  int y2 = analogRead(Eje_Y2);
  int x3 = analogRead(Eje_X3);
  int y3 = analogRead(Eje_Y3);

  // Control Joystick 1
  if (x1 < 400)       angulo1 -= salto;
  else if (x1 > 600)  angulo1 += salto;

  if (y1 < 400)       angulo3 += salto;
  else if (y1 > 600)  angulo3 -= salto;

  // Control Joystick 2
  if (x2 < 400)       angulo2 += salto;
  else if (x2 > 600)  angulo2 -= salto;

  if (y2 < 400)       angulo4 -= salto;
  else if (y2 > 600)  angulo4 += salto;

  // Control Joystick 3
  if (x3 < 400)       angulo5 += salto;
  else if (x3 > 600)  angulo5 -= salto;

  if (y3 < 400)       angulo6 -= salto;
  else if (y3 > 600)  angulo6 += salto;

  // Limitar ángulos entre 0 y 180 grados mediante constrain
  angulo1 = constrain(angulo1, 0, 180);
  angulo2 = constrain(angulo2, 0, 180);
  angulo3 = constrain(angulo3, 0, 180);
  angulo4 = constrain(angulo4, 0, 180);
  angulo5 = constrain(angulo5, 0, 180);
  angulo6 = constrain(angulo6, 0, 180);

  // Enviar ángulos a los servos
  servo1.write(angulo1);
  servo2.write(angulo2);
  servo3.write(angulo3);
  servo4.write(angulo4);
  servo5.write(angulo5);
  servo6.write(angulo6);

  // Monitoreo Serie
  Serial.print("S1: "); Serial.print(angulo1); Serial.print(" | ");
  Serial.print("S2: "); Serial.print(angulo2); Serial.print(" | ");
  Serial.print("S3: "); Serial.print(angulo3); Serial.print(" | ");
  Serial.print("S4: "); Serial.print(angulo4); Serial.print(" | ");
  Serial.print("S5: "); Serial.print(angulo5); Serial.print(" | ");
  Serial.print("S6: "); Serial.println(angulo6);

  delay(50); // Controla la velocidad de refresco del movimiento
}