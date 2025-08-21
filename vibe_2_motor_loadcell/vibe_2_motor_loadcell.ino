//###################################################
//# This program made by Park Younghoon [Blind - X] #
//# for the blind people who can't see their weight #
//###################################################
#include "HX711.h"

// HX711 circuit wiring
const int LOADCELL_DOUT_PIN = 2;
const int LOADCELL_SCK_PIN = 3;

// vibrate motorw
#define VIB_MOT_1_HIGH  9
#define VIB_MOT_1_LOW   8
#define VIB_MOT_2_HIGH  11
#define VIB_MOT_2_LOW   10
#define VIB_MOT_1_PWM 5
#define VIB_MOT_2_PWM 6
#define VIB_MOT_1_2_PWM 78
HX711 scale;
void setup() {
   pinMode(VIB_MOT_1_PWM, OUTPUT);
   pinMode(VIB_MOT_2_PWM, OUTPUT);
   pinMode(VIB_MOT_1_HIGH, OUTPUT);
   pinMode(VIB_MOT_1_LOW, OUTPUT);
   pinMode(VIB_MOT_2_HIGH, OUTPUT);
   pinMode( VIB_MOT_2_LOW, OUTPUT);
   digitalWrite(VIB_MOT_1_HIGH,HIGH);
   digitalWrite(VIB_MOT_2_HIGH,HIGH);
   digitalWrite(VIB_MOT_1_LOW,LOW);
   digitalWrite(VIB_MOT_2_LOW,LOW);
   Serial.begin(9600);
   scale.begin(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN);
}


long row_value_from_scale = 0;
int receivedNumber = 0;

void loop() {
  int mode = 1 ;
  

  if (mode)
  {
        Serial.print("row data : ");
        Serial.print(row_value_from_scale);
        Serial.print("cal data : ");
        Serial.println(calibrate_scale(row_value_from_scale));
      if(read_scale())
      {
        
        // read data from scale ;
        receivedNumber = calibrate_scale(row_value_from_scale);
      }
  }
  else
  {
    if (Serial.available() > 0) 
    { 
      // int data parcing
      receivedNumber = Serial.parseInt(); 
      Serial.print("Received number: ");
      Serial.println(receivedNumber);
    }
  }

   if(receivedNumber != 0) 
      {
        // make received data to xxx.x form and save it array.
        char weight[6];
        make_weight(receivedNumber,weight);
        Serial.print("this is your weight !! : ");
        Serial.println(weight); 
        
        //input xxx.x data to viberation program.
        //patern_1(weight);
        patern_2(weight);
        receivedNumber = 0;
      }
}

// make the weight string 
void make_weight(int num, char * str)
{
  str[0] = num / 1000 + '0'; 
  str[1] = num % 1000 /100+ '0';
  str[2] = num %100 /10+ '0';
  str[3] = '.';
  str[4] = num %10+ '0';
  str[5] = '\0';
}
