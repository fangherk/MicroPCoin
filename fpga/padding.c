//
// Herrick Fang, Teerapat Jenrungrot 
// 11/25/2017
// padding.c section 5.1.1

#include <stdio.h>

unsigned int findK(unsigned int l){
  // Find k to satisfy the equivalence relation:
  // l+1+k === 448 mod 512

  unsigned int total = l + 1;
  unsigned int k;
  
  // Deal with the less than 448 case
  if (total < 448){
    k = 448 - total;
  }else{
    // Deal with > 448 case 
    unsigned modded = total % 512;
    if(modded > 448 && modded < 512){
      // go to the next mod value up
      k = 960 - modded;
    }else{ // modded < 512
      // just add up to 448 
      k = 448 - modded;
    }
  }
  return k;
}

int main()
{
  // Add the python message here.
  unsigned char msg[2048] = "abc";
  unsigned int i, l=0;

  // Generate the ith value of the char array
  // Gather the number of char bits as well
  i = 0;
  while(msg[i] != '\0'){
    l+=8;
    i++;
  }
  printf("i: %d, l: %d", i, l);

  
  // Find the equivalence relation value for k
  // to satisfy l + 1 + k === 448 mod 512
  unsigned int k = findK(l);
  printf("l: %d\nk: %d\nl+1+k: %d\nl+1+k mod 512: %d\n",l,k,l+1+k, (l+1+k)%512);


  // Add a 1 bit to the end of the message.
  // Assume k is larger than 7. Is this a safe assumption?
  // Then, we should get
  unsigned char tmp1 = 0x80;
  unsigned char tmp0 = 0x00;
  strncat(msg, &tmp1, 1);
  i++;
  

  // Append k zeros
  int leftovers = (k+1) - 8;
  int z;
  int limitPt = leftovers/8;
  if (k != 7){
    // printf("leftovers %d\n", limitPt);
    while( z != limitPt){
      printf("z: %d\n", z);
      msg[i] = tmp0;
      i++;
      z++;
    }
  }

 
  // Append 64 bits to the end
  unsigned char temp64[8];
  unsigned long long appendBits = l;
  unsigned int j;
 
  for(j=0; j < 8; j++){
    temp64[j] = (appendBits << (j*8)) & 0xFF;
  }

  for(j=0; j < 8; j++){
    msg[i] = temp64[7-j];
    i++;
  }

  // Add the last terminating string
  msg[i] = '\0';
  // possibly off by 1? Should we increase by 1

  //Print out the resulting value
  
  unsigned int p = 0;
  while(p < i){
    printf("\nmsg %d: %02x", p, msg[p]);
    p++;
  }
  

  printf("\nDone!");

    
  return 0;
}

