#include "HX711.h"
int read_scale() 
{

  static int i = 0 ;
  if (scale.is_ready()) 
  {
    row_value_from_scale = scale.read();
    static long last_time = 0;
    
    if(row_value_from_scale> 1000000) 
    {
      i++;
      last_time = millis();
    }
    if(millis() - last_time > 2000) 
    {
      i = 0;
    }
    if( i > 25 ) 
    {
      i = 0;
      return 1;
    }
    //Serial.print("HX711 reading: ");
    //Serial.println(reading);
  } 
  else 
  {
    //Serial.println("HX711 not found.");
  }
 
  delay(100);

  return 0;
}

int calibrate_scale(long data)
{
  // a third-order polynomial
  // a*x^3 + b*x^2  + c*x^1 + d
  
  const float a = 0;
  const float b = 0;
  const float c = 0.00005;
  const float d = -8.55556;
  float value = a * pow(data,3) + b * pow(data,2) + c * data + d ; 
  return value*10;
}
