#include <LiquidCrystal.h>
#include <Wire.h>

#define SLAVE_ADDRESS 0x04

int number = 0;
String str;

LiquidCrystal lcd(12, 11, 5, 4, 3, 2);

void setup() {
  pinMode(13, OUTPUT);
  Wire.begin(SLAVE_ADDRESS);
  Wire.onReceive(receiveData);
  lcd.begin(16, 2);
  lcd.print("   WiFighter");
}

void loop() {
  delay(500);
}

void receiveData(int byteCount){
  for (int i=0 ; i <= byteCount ; i++){
    char d = Wire.read();
    if (d == 0){
      lcd.clear();
      return;
    }
    else if (d == 1){
      lcd.setCursor(0, 0);
      return;
    }
    else if (d == 2){
      lcd.setCursor(0, 1);
      return;
    }
    else if (d == 32){
      lcd.print(' ');
    }
    else if (d >= '0' && d <= 'z'){
      lcd.print(d);
    }
  }
}
