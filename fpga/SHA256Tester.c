/******************************************************************************

                            Online C Compiler.
                Code, Compile, Run and Debug C program online.
Write your code in this editor and press "Run" button to compile and execute it.

*******************************************************************************/

#include <stdio.h>

unsigned int rotr(unsigned int val, unsigned  int n){
    return (val >> n) | (val << 32-n); 
}
unsigned int sigma_1(unsigned int x){
    //printf("x=%08x\trotr(x,17) = %08x\trotr(x,19) = %08x\tx>>10 = %08x\t" ,x,rotr(x, 6),rotr(x, 11),x>>10 );
    return rotr(x, 17) ^ rotr(x, 19) ^ (x >> 10);
}


    
unsigned  int sigma_0(unsigned int x){
    return rotr(x, 7) ^ rotr(x, 18) ^ (x >> 3);
}

unsigned int bigSigma_1(unsigned int x){
    //printf("x=%08x\trotr(x,6) = %08x\trotr(x,11) = %08x\trotr(x,25) = %08x\t" ,x,rotr(x, 6),rotr(x, 11),rotr(x, 25) );
    return rotr(x, 6) ^ rotr(x, 11) ^ rotr(x, 25);
}

unsigned int bigSigma_0(unsigned int x){
    return rotr(x, 2) ^ rotr(x, 13) ^ rotr(x, 22);
}

unsigned int bigCh(unsigned int x, unsigned int y, unsigned int z){
    return (x & y) ^ (~x & z);
}

unsigned int bigMaj(unsigned int x, unsigned int y, unsigned int z){
    return (x&y) ^ (x&z) ^ (y&z);
}


int main()
{
    unsigned int W[64] = {};
    unsigned int K[64] = {};
    unsigned int i = 0, j = 0, k = 0;
    unsigned int a,b,c,d,e,f,g,h,t1,t2;
    unsigned int h0,h1,h2,h3,h4,h5,h6,h7;
    W[0]=  0x61626380;
    W[1]=  0x00000000;
    W[2]=  0x00000000;
    W[3]=  0x00000000;
    W[4]=  0x00000000;
    W[5]=  0x00000000;
    W[6]=  0x00000000;
    W[7]=  0x00000000;
    W[8]=  0x00000000;
    W[9]=  0x00000000;
    W[10]= 0x00000000;
    W[11]= 0x00000000;
    W[12]= 0x00000000;
    W[13]= 0x00000000;
    W[14]= 0x00000000;
    W[15]= 0x00000018;
    
    a = 0x6a09e667;
    b = 0xbb67ae85;
    c = 0x3c6ef372;
    d = 0xa54ff53a;
    e = 0x510e527f;
    f = 0x9b05688c;
    g = 0x1f83d9ab;
    h = 0x5be0cd19;
    
    h0 = a;
    h1=b;
    h2=c;
    h3=d;
    h4=e;
    h5=f;
    h6=g;
    h7=h;
    
    K[0] = 0x428a2f98;
    K[1] = 0x71374491;
    K[2] = 0xb5c0fbcf ;
    K[3] = 0xe9b5dba5 ;
    K[4] = 0x3956c25b ;
    K[5] = 0x59f111f1 ;
    K[6] = 0x923f82a4 ;
    K[7] = 0xab1c5ed5 ;
    K[8] = 0xd807aa98 ;
    K[9] = 0x12835b01 ;
    K[10] = 0x243185be ;
    K[11] = 0x550c7dc3 ;
    K[12] = 0x72be5d74 ;
    K[13] = 0x80deb1fe ;
    K[14] = 0x9bdc06a7 ;
    K[15] = 0xc19bf174 ;
    K[16] = 0xe49b69c1 ;
    K[17] = 0xefbe4786 ;
    K[18] = 0x0fc19dc6 ;
    K[19] = 0x240ca1cc ;
    K[20] = 0x2de92c6f ;
    K[21] = 0x4a7484aa ;
    K[22] = 0x5cb0a9dc ;
    K[23] = 0x76f988da ;
    K[24] = 0x983e5152 ;
    K[25] = 0xa831c66d ;
    K[26] = 0xb00327c8 ;
    K[27] = 0xbf597fc7 ;
    K[28] = 0xc6e00bf3 ;
    K[29] = 0xd5a79147 ;
    K[30] = 0x06ca6351 ;
    K[31] = 0x14292967;
    K[32] = 0x27b70a85 ;
    K[33] = 0x2e1b2138 ;
    K[34] = 0x4d2c6dfc ;
    K[35] = 0x53380d13 ;
    K[36] = 0x650a7354 ;
    K[37] = 0x766a0abb ;
    K[38] = 0x81c2c92e ;
    K[39] = 0x92722c85 ;
    K[40] = 0xa2bfe8a1 ;
    K[41] = 0xa81a664b ;
    K[42] = 0xc24b8b70 ;
    K[43] = 0xc76c51a3 ;
    K[44] = 0xd192e819 ;
    K[45] = 0xd6990624 ;
    K[46] = 0xf40e3585 ;
    K[47] = 0x106aa070 ;
    K[48] = 0x19a4c116 ;
    K[49] = 0x1e376c08 ;
    K[50] = 0x2748774c ;
    K[51] = 0x34b0bcb5 ;
    K[52] = 0x391c0cb3 ;
    K[53] = 0x4ed8aa4a ;
    K[54] = 0x5b9cca4f ;
    K[55] = 0x682e6ff3 ;
    K[56] = 0x748f82ee ;
    K[57] = 0x78a5636f ;
    K[58] = 0x84c87814 ;
    K[59] = 0x8cc70208 ;
    K[60] = 0x90befffa ;
    K[61] = 0xa4506ceb ;
    K[62] = 0xbef9a3f7 ;
    K[63] = 0xc67178f2 ;

    
    for(i; i < 64; i++){
        if(i <16){
            continue;
        }else{
            W[i] = sigma_1(W[i-2]) + W[i-7] + sigma_0(W[i-15]) + W[i-16];
             printf("round k= %d\n",i);
            printf("Sigma 1 = %08x\t Sigma 0 = %08x\n\tW[i-2] = %08x\n\tw[i-15] = %08x\n", sigma_1(W[i-2]),sigma_0(W[i-15]), W[i-2], W[i-15]);
        }
    }
     printf("a=%08x\tb=%08x\tc=%08x\td=%08x\te=%08x\t\nf=%08x\tg=%08x\th=%08x\n\n\n" , a,b,c,d,e,f,g,h);
    for(k; k < 64; k++){
        //printf("h=%08x\tsigma=%08x\tch=%08x\tw=%08x\tk=%08x\n\n", h,bigSigma_1(e),bigCh(e,f,g),W[k],K[k]);
        //printf("e=%08x\t\n", e);
        t1 = h + bigSigma_1(e) + bigCh(e,f,g) + W[k] + K[k];
        t2 = bigSigma_0(a) + bigMaj(a,b,c);
        h=g;
        g=f;
        f=e;
        e=d+t1;
        d=c;
        c=b;
        b=a;
        a=t1+t2;
        printf("round k= %d\n",k);
        //printf("w= %08x\n",W[k]);
        printf("a=%08x\tb=%08x\tc=%08x\td=%08x\te=%08x\t\nf=%08x\tg=%08x\th=%08x\nt1=%08x\nt2=%08x\tw=%08x\tk=%08x\t\n\n" , a,b,c,d,e,f,g,h,t1,t2,W[k],K[k]);
        // h0 = a + h0;
        // h1 = b + h1;
        // h2 = c + h2;
        // h3 = d + h3;
        // h4 = e + h4;
        // h5 = f + h5;
        // h6 = g + h6;
        // h7 = h + h7;
       //printf("h0=%08x\thp1=%08x\th2=%08x\th3=%08x\th4=%08x\t\nh5=%08x\th6=%08x\th7=%08x\n\n\n" , h0,h1,h2,h3,h4,h5,h6,h7);
    }
    
    h0 = a + h0;
    h1 = b + h1;
    h2 = c + h2;
    h3 = d + h3;
    h4 = e + h4;
    h5 = f + h5;
    h6 = g + h6;
    h7 = h + h7;
    printf("h0=%08x\thp1=%08x\th2=%08x\th3=%08x\th4=%08x\t\nh5=%08x\th6=%08x\th7=%08x\n\n\n" , h0,h1,h2,h3,h4,h5,h6,h7);
    // for(j; j < 64; j++){
    //     printf("j = %d \t %08x\n" , j, W[j]);
    // }
    
    

    return 0;
}



