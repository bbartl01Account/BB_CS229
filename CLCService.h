/****************************************************************************

  Header file for template service
  based on the Gen 2 Events and Services Framework

 ****************************************************************************/

#ifndef CLCService_H
#define CLCService_H

#include "ES_Types.h"

// Public Function Prototypes

bool InitCLCService(uint8_t Priority);
bool PostCLCService(ES_Event_t ThisEvent);
ES_Event_t RunCLCService(ES_Event_t ThisEvent);

#define MAX_RPM 53
#define MIN_RPM 11
#define RPM_DIFF 42

typedef union{
    uint32_t FullTime;
    uint16_t ByBytes[2];
}TimeTicks_t;

uint16_t GetRPM(void);
uint16_t GetDutyCycle(void);

#endif /* ServTemplate_H */

