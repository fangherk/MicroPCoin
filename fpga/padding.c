//
// Herrick Fang, Teerapat Jenrungrot 
// 11/25/2017
// padding.c section 5.1.1

#include <stdio.h>
#include <string.h>
unsigned int findK(unsigned int l){
    return (((448 - l -1) % 512) + 512) % 512;
}

unsigned long long swapBytesOrder(unsigned long long val){
    unsigned long long answer = 0;
    unsigned char buffer[20];
    int i,j;
    for(i=0;i<8;i++){
        buffer[i] = (val & (0xFFULL << (i << 3))) >> (i << 3);
    }
    for(i=7,j=0;i>=0;i--,j++){
        answer |= ((unsigned long long)buffer[i] << (j << 3));
    }
    return answer; 
}

int main()
{

  unsigned char output[2048];
  memset(output, 0, sizeof(output));
  // Add the python message here.
//  unsigned char msg[2048] = "abc";
  unsigned char msg[2048] = "abcdefghbcdefghicdefghijdefghijkefghijklfghijklmghijklmnhijklmnoijklmnopjklmnopqklmnopqrlmnopqrsmnopqrstnopqrstu";
  unsigned int i;
  unsigned long long l=0LL;
  // Generate the ith value of the char array
  // Gather the number of char bits as well
  i = 0;

  while(msg[i] != '\0'){
    output[i] = msg[i];
    output[i+1] = 0x80;
    l+=8LL;
    i++;
  }

  printf("i: %d, l: %d", i, l);

  
  // Find the equivalence relation value for k
  // to satisfy l + 1 + k === 448 mod 512
  unsigned int k = findK(l);
  printf("l: %d\nk: %d\nl+1+k: %d\nl+1+k mod 512: %d\n",l,k,l+1+k, (l+1+k)%512);
  printf("%x %lld\n",l, l);
  printf("%lx\n", swapBytesOrder(l)); 
  unsigned long long* lengthPosition = (unsigned long long*)(output + ((l + 1 + k) >> 3));
  *lengthPosition = swapBytesOrder(l);

  
  unsigned int p = 0;
  while(p < ((l+1+k+64)>>3)){
    printf("%02x", output[p]);
    p++;
  }
  

  printf("\nDone!");

    
  return 0;
}

