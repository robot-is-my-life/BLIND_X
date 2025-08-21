
// Input pin_number, power, duty[ms]
void pulse(int PIN,int POWER,int duty_HIGH,int duty_LOW){
  if(PIN == VIB_MOT_1_2_PWM) 
  {
    analogWrite(VIB_MOT_1_PWM,POWER);
    analogWrite(VIB_MOT_2_PWM,POWER);
  }
  else analogWrite(PIN,POWER);
  
  delay(duty_HIGH);
  analogWrite(VIB_MOT_1_PWM,0);
  analogWrite(VIB_MOT_2_PWM,0);
  delay(duty_LOW);
  Serial.println("vibe!");
}

// patern 1
// only timing 
void patern_1(char * num)
{
  const int in_number_vibe_time_ms  = 400;
  const int in_number_delay_time_ms  = 400;
  const int num_to_num_delay_time_ms = 1000;
  const int dot_vibe_time_ms        = 1000;
  const int power_of_vibe       = 150;
  for(int i = 0 ; i < 5; i++)
  {
    Serial.print("num : ");
    Serial.println(num[i]);
    // if dot
    if(num[i] == '.') 
    {
      pulse(VIB_MOT_1_PWM,power_of_vibe,dot_vibe_time_ms,num_to_num_delay_time_ms);
      continue;
    }

    // vibrate motor each number
    for(int z = 0 ; z < num[i] - '0'; z++)
    {
      pulse(VIB_MOT_1_PWM,power_of_vibe,in_number_vibe_time_ms,in_number_delay_time_ms);
    }

    
    delay(num_to_num_delay_time_ms);
  }
  
}


// patern 2
// Use two motor
void patern_2(char * num)
{
  const int in_number_vibe_time_ms  = 150;
  const int in_number_delay_time_ms  = 100;
  const int num_to_num_delay_time_ms = 1000;
  const int dot_vibe_time_ms        = 1000;
  const int power_of_vibe       = 140;
  for(int i = 0 ; i < 5; i++)
  {
    Serial.print("num : ");
    Serial.println(num[i]);
    // if dot
    if(num[i] == '.') 
    {
      pulse(VIB_MOT_1_2_PWM,power_of_vibe,dot_vibe_time_ms,num_to_num_delay_time_ms);
      continue;
    }
    else
    {
      // vibrate motor each number
      for(int z = 0 ; z < num[i] - '0'; z++)
      {
        // The hundredth digit number
        if(i == 0) 
        pulse(VIB_MOT_1_2_PWM,power_of_vibe,in_number_vibe_time_ms,in_number_delay_time_ms);
        
        // The ten digit number
        else if(i == 1)
        pulse(VIB_MOT_1_PWM,power_of_vibe,in_number_vibe_time_ms,in_number_delay_time_ms);
        
        // The one digit number
        else if(i == 2)
        pulse(VIB_MOT_2_PWM,power_of_vibe,in_number_vibe_time_ms,in_number_delay_time_ms);
  
        // The one decimal place.
        else if(i == 4)
        pulse(VIB_MOT_1_2_PWM,power_of_vibe,in_number_vibe_time_ms,in_number_delay_time_ms);
      }
    }
    

    delay(num_to_num_delay_time_ms);
  }
  
}
