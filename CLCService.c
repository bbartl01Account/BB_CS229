/****************************************************************************
 Module
   TemplateService.c

 Revision
   1.0.1

 Description
   This is a template file for implementing a simple service under the
   Gen2 Events and Services Framework.

 Notes

 History
 When           Who     What/Why
 -------------- ---     --------
 01/16/12 09:58 jec      began conversion from TemplateFSM.c
****************************************************************************/
/*----------------------------- Include Files -----------------------------*/
/* include header files for this state machine as well as any machines at the
   next lower level in the hierarchy that are sub-machines to this machine
*/
#include "ES_Configure.h"
#include "ES_Framework.h"
#include "CLCService.h"
#include "PIC32_AD_Lib.h"
#include <xc.h>
#include <sys/attribs.h>
#include "dbprintf.h"

/*----------------------------- Module Defines ----------------------------*/
#define ZN_TESTING

#define K_P 1
#define K_I 0.1
#define K_D 1

#define PR_P1 2170

#define TICK_FREQ 20000000/4
#define PPR 512
#define RED 5.9

#define TICK_2_RPM 60*TICK_FREQ/(PPR*RED)

#define AD_CHANNEL BIT5HI

#define OSCOPE LATBbits.LATB14

#define STEP_VALUE 30 //RPM
#define MAX_IDX 5000
/*---------------------------- Module Functions ---------------------------*/
/* prototypes for private functions for this service.They should be functions
   relevant to the behavior of this service
*/

/*---------------------------- Module Variables ---------------------------*/
// with the introduction of Gen2, we need a module level Priority variable
static uint8_t MyPriority;
volatile uint16_t CapturedTime;
volatile static uint16_t RolloverCounter;
volatile static TimeTicks_t CurrentVal;
volatile static uint32_t PrevVal;
volatile static uint32_t DeltaTicks;
volatile static float RPM;
volatile static float Error;
volatile static float ErrorSum;
volatile static float PrevError;
static float TargetRPM;
volatile static float DC_Percent;
static uint32_t POTval[1];
//volatile static uint16_t ICcounter;

#ifdef ZN_TESTING
static uint8_t RPMArray[MAX_IDX];
static uint16_t idx;
#endif

/*------------------------------ Module Code ------------------------------*/
/****************************************************************************
 Function
     InitTemplateService

 Parameters
     uint8_t : the priorty of this service

 Returns
     bool, false if error in initialization, true otherwise

 Description
     Saves away the priority, and does any
     other required initialization for this service
 Notes

 Author
     J. Edward Carryer, 01/16/12, 10:00
****************************************************************************/
bool InitCLCService(uint8_t Priority)
{
  ES_Event_t ThisEvent;

  MyPriority = Priority;
  /********************************************
   in here you write your initialization code
   *******************************************/
  //Make RB10 a digital input to read the encoder and map it to IC2
  TRISBbits.TRISB10 = 1;
  IC2R = 0b0011;
  
  // Since we only drive one direction and don't want to change the circuit,
  // make RB4 a digial output and tie it low
  TRISBbits.TRISB4 = 0;
  LATBbits.LATB4 = 0;
  
  // Make RB8 a digital output for PWM and map OC2 to it
  TRISBbits.TRISB8 = 0;
  RPB8R = 0b0101;
  
  // Make RB14 a digital output for timing reading
  TRISBbits.TRISB14 = 0;
  ANSELBbits.ANSB14 = 0;
  OSCOPE = 0;
  
  // Initialize RB3 to read the potentiometer
  TRISBbits.TRISB3 = 1;
  ANSELBbits.ANSB3 = 1;
  ADC_ConfigAutoScan(AD_CHANNEL);
  
  // Set several variables to 0 to initialize them
  CurrentVal.FullTime = 0;
  PrevVal = 0;
  CapturedTime = 0xBEEF;
  RolloverCounter = 0;
  DeltaTicks = 0;
  Error = 0;
  ErrorSum = 0;
  PrevError = 0;
  TargetRPM = 0;
  //ICcounter = 0;
  
  // Configure Timer 3 to be used for Output Capture
  // Disable Timer 3
  T3CONbits.ON = 0;
  // Select the internal clock as the source
  T3CONbits.TCS = 0;
  // Select a 1:2 prescaler
  T3CONbits.TCKPS = 0b001;
  // Have the timer start at 0
  TMR3 = 0;
  // Set the period register
  PR3 = PR_P1 - 1;
  // Clear the interrupt flag for Timer 3
  IFS0CLR = _IFS0_T3IF_MASK;
  // Disable interrupts on Timer 3
  IEC0CLR = _IEC0_T3IE_MASK;
  // Enable Timer 3
  T3CONbits.ON = 1;
  
  // Configure OC2
  // Disable OC2
  OC2CONbits.ON = 0;
  // Specify that a 16 bit timer is being used
  OC2CONbits.OC32 = 0;
  // Specify that Timer 3 is the source
  OC2CONbits.OCTSEL = 1;
  // Specify PWM Mode, fault pin disabled
  OC2CONbits.OCM = 0b110;
  // Set the initial duty cycle to 0 (initial setting requires both OCxR and OCxRS)
  OC2R = 0;
  OC2RS = 0;
  // Enable OC2
  OC2CONbits.ON = 1;
  
  // Configure Timer 2 (to be used for Input Capture)
  // Disable Timer 2
  T2CONbits.ON = 0;
  // Select the internal clock as the source
  T2CONbits.TCS = 0;
  //T2CONbits.TGATE = 0; //added
  // Choose a 1:4 prescaler
  T2CONbits.TCKPS = 0b010;
  // Set the initial value of the timer to 0
  TMR2 = 0;
  // Set the Period Register value to the max
  PR2 = 0xFFFF;
  // Clear the Timer 2 interrupt flag
  IFS0CLR = _IFS0_T2IF_MASK;
  // Set the priority of the Timer 2 interrupt to 6
  IPC2bits.T2IP = 6;
  // Enable interrupts from Timer 2
  IEC0SET = _IEC0_T2IE_MASK;
  // Enable Timer 2
  T2CONbits.ON = 1;
  
  // Configure Input Capture
  // Disable IC2
  IC2CONbits.ON = 0;
  // Specify a 16 bit timer
  IC2CONbits.C32 = 0;
  // Select Timer 2
  IC2CONbits.ICTMR = 1;
  // Configure to interrupt on every capture event
  IC2CONbits.ICI = 0;
  // Configure to interrupt on every rising edge
  IC2CONbits.ICM = 0b011;
  // Enable IC2
  IC2CONbits.ON = 1;
  // Read the IC2 buffer into a variable
    do{
        CapturedTime = (uint16_t)IC2BUF;
    }while(IC2CONbits.ICBNE != 0);
  // Clear the interrupt flag for IC2
  IFS0CLR = _IFS0_IC2IF_MASK;
//  DB_printf("ICBNE: %u\n",IC2CONbits.ICBNE);
//  DB_printf("IC Flag: %u\n",IFS0bits.IC4IF);
//  DB_printf("\n");
  // Set the priority of the IC2 interrupt to 7
  IPC2bits.IC2IP = 7;
  // Enable interrupts from IC2
  IEC0SET = _IEC0_IC2IE_MASK;
  
  
  // Configure Timer 4 as an interrupt to implement the control law
  // Disable Timer 4
  T4CONbits.ON = 0;
  // Select the internal clock as the source
  T4CONbits.TCS = 0;
  //T2CONbits.TGATE = 0; //added
  // Choose a 1:2 prescaler
  T4CONbits.TCKPS = 0b001;
  // Set the initial value of the timer to 0
  TMR4 = 0;
  // Set the Period Register to interrupt every 2 ms
  PR4 = 19999;
  // Clear the Timer 4 interrupt flag
  IFS0CLR = _IFS0_T4IF_MASK;
  // Set the priority of the Timer 4 interrupt to 6
  IPC4bits.T4IP = 6;
  // Enable interrupts from Timer 4
  IEC0SET = _IEC0_T4IE_MASK;
  // Enable Timer 4
  T4CONbits.ON = 1;
  
#ifdef ZN_TESTING
  idx = 0;
  RPM = 0;
  
  T5CONbits.ON = 0;
  T5CONbits.TCS = 0;
  T5CONbits.TCKPS = 0b001;
  TMR5 = 0;
  PR5 = 9999;
  IFS0CLR = _IFS0_T4IF_MASK;
  IPC5bits.T5IP = 6;
  IEC0SET = _IEC0_T5IE_MASK;
  T5CONbits.ON = 1;
#endif
  
  // Enable interrupts globally
  __builtin_enable_interrupts();
  
#ifndef ZN_TESTING
  // Start the timer for when to read the POT next
  ES_Timer_InitTimer(AD_TIMER,ONE_SEC*0.1);
#endif
  
  // post the initial transition event
  ThisEvent.EventType = ES_INIT;
  if (ES_PostToService(MyPriority, ThisEvent) == true)
  {
    return true;
  }
  else
  {
    return false;
  }
}

/****************************************************************************
 Function
     PostTemplateService

 Parameters
     EF_Event_t ThisEvent ,the event to post to the queue

 Returns
     bool false if the Enqueue operation failed, true otherwise

 Description
     Posts an event to this state machine's queue
 Notes

 Author
     J. Edward Carryer, 10/23/11, 19:25
****************************************************************************/
bool PostCLCService(ES_Event_t ThisEvent)
{
  return ES_PostToService(MyPriority, ThisEvent);
}

/****************************************************************************
 Function
    RunTemplateService

 Parameters
   ES_Event_t : the event to process

 Returns
   ES_Event, ES_NO_EVENT if no error ES_ERROR otherwise

 Description
   add your description here
 Notes

 Author
   J. Edward Carryer, 01/15/12, 15:23
****************************************************************************/
ES_Event_t RunCLCService(ES_Event_t ThisEvent)
{
  ES_Event_t ReturnEvent;
  ReturnEvent.EventType = ES_NO_EVENT; // assume no errors
  /********************************************
   in here you write your service code
   *******************************************/
  if(ES_TIMEOUT == ThisEvent.EventType){
      if(AD_TIMER == ThisEvent.EventParam){
          ADC_MultiRead(POTval);
          TargetRPM = MAX_RPM*POTval[0]/1023;
          DB_printf("TargetRPM: %u\n",(uint16_t)TargetRPM);
          DB_printf("Actual RPM: %u\n",(uint16_t)RPM);
          DB_printf("DC: %u\n",(uint16_t)DC_Percent);
          DB_printf("\n");
          ES_Timer_InitTimer(AD_TIMER,ONE_SEC*0.1);
      }else if(PRINT_TIMER == ThisEvent.EventParam){
#ifdef ZN_TESTING
          DB_printf("%u,%u\n",idx,RPMArray[idx]);
          idx++;
          if(MAX_IDX > idx){
            ES_Timer_InitTimer(PRINT_TIMER,1);
          }
#endif
      }
  }
  return ReturnEvent;
}

/***************************************************************************
 private functions
 ***************************************************************************/
uint16_t GetRPM(void){
    return (uint16_t)RPM;
}

uint16_t GetDutyCycle(void){
    return (uint16_t)DC_Percent;
}

void __ISR(_INPUT_CAPTURE_2_VECTOR,IPL7SOFT) IC2ISR(void){
    // Read the IC2 buffer into a variable
    do{
        CapturedTime = (uint16_t)IC2BUF;
    }while(IC2CONbits.ICBNE != 0);
    // Clear the interrupt flag for IC2
    IFS0CLR = _IFS0_IC2IF_MASK;
    // If a rollover has occurred and the Timer 2 interrupt flag is still set
    if((0x8000 > CapturedTime) && (1 == IFS0bits.T2IF)){
        // Increment the rollover counter
        RolloverCounter++;
        // Clear the Timer 2 interrupt flag
        IFS0CLR = _IFS0_T2IF_MASK;
    }
    // Set the lower 16 bits of CurrentVal equal to the captured value
    CurrentVal.ByBytes[0] = CapturedTime;
    // Set the upper 16 bits of CurrentVal equal to the rollover counter
    CurrentVal.ByBytes[1] = RolloverCounter;
    // Compute the period (in ticks) between two pulses
    DeltaTicks = CurrentVal.FullTime - PrevVal;
    // Set the previous period equal to the current period
    PrevVal = CurrentVal.FullTime;
    // Convert the tick period into RPM
    RPM = TICK_2_RPM/DeltaTicks;
    //ICcounter++;
}

void __ISR(_TIMER_2_VECTOR,IPL6SOFT) Timer2_ISR(void){
    // Disable interrupts globally
    __builtin_disable_interrupts();
    // If the Timer 2 interrupt flag is set
    if(1 == IFS0bits.T2IF){
        // Increment the rollover counter
        RolloverCounter++;
        // Clear the Timer 2 interrupt flag
        IFS0CLR = _IFS0_T2IF_MASK;
    }
    // Enable interrupts globally
    __builtin_enable_interrupts();
}

void __ISR(_TIMER_4_VECTOR,IPL6SOFT) CLC_ISR(void){
    // Raise the OSCOPE pin to begin timing
    OSCOPE = 1;
    // Clear the Timer 2 interrupt flag
    IFS0CLR = _IFS0_T4IF_MASK;
    // Compute the error in attaining the target velocity
    Error = TargetRPM - RPM;
    // Add to the sum of errors over time
    ErrorSum += Error;
    // Compute the required duty cycle
    DC_Percent = K_P*Error + K_I*ErrorSum + K_D*(Error - PrevError);
    // Convert the duty cycle into the tick value for OC2RS
    // Account for saturation
    if(100 < DC_Percent){
        DC_Percent = 100;
        ErrorSum -= Error;
    }else if(0 > DC_Percent){
        DC_Percent = 0;
        ErrorSum -= Error;
    }
    PrevError = Error;
    OC2RS = (uint16_t)DC_Percent*PR_P1/100;
    // Lower the OSCOPE pin to end timing
    OSCOPE = 0;
}

#ifdef ZN_TESTING
void __ISR(_TIMER_5_VECTOR,IPL6SOFT) ZN_ISR(void){
    IFS0CLR = _IFS0_T5IF_MASK;
    if(0 == TargetRPM){
        TargetRPM = STEP_VALUE;
    }
    RPMArray[idx] = (uint8_t)RPM;
    idx++;
    if(MAX_IDX <= idx){
        idx = 0;
        ES_Timer_InitTimer(PRINT_TIMER,ONE_SEC*0.1);
        T5CONbits.ON = 0;
    }
}
#endif
/*------------------------------- Footnotes -------------------------------*/
/*------------------------------ End of file ------------------------------*/

