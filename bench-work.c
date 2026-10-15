/* Reproducible paired benchmark; see reproduce.py. SPDX-License-Identifier: curl */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <assert.h>
#include "corpus.h"
#include "zones.h"
#define N 1024
#define REPS 256
#define ROUNDS 21
int base_checkday(const char *, size_t);
int base_checkmonth(const char *, size_t);
int pack_checkday(const char *, size_t);
int pack_checkmonth(const char *, size_t);
int base_unit_checktz(const char *, size_t);
int pack_unit_checktz(const char *, size_t);
time_t base_curl_getdate(const char *, const time_t *);
time_t pack_curl_getdate(const char *, const time_t *);
static uint32_t state = 0x20261015;
static volatile uint64_t sink;
static uint32_t rnd(void) { state ^= state << 13; state ^= state >> 17; state ^= state << 5; return state; }
static const char *months[] = {"Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"};
static const char *days[] = {"Mon","Tue","Wed","Thu","Fri","Sat","Sun"};
static const char *full[] = {"Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"};
struct item { char s[128]; size_t len; };
struct workload { const char *name; int kind; struct item data[N]; };
static struct workload work[] = {
 {"month-valid",0}, {"day-valid",1}, {"day-full",1},
 {"month-invalid-ascii",0}, {"day-invalid-ascii",1},
 {"month-nearmiss",0}, {"day-nearmiss",1}, {"month-short",0}, {"day-short",1},
 {"parser-corpus-random",2}, {"parser-valid-corpus",2}, {"parser-invalid-corpus",2},
 {"parser-rfc1123",2}, {"parser-rfc850",2}, {"parser-asctime",2}, {"parser-numeric",2},
 {"month-wrong-first",0}, {"day-wrong-first",1},
 {"tz-gmt",3}, {"tz-utc",3}, {"tz-other-three",3}, {"tz-four",3},
 {"tz-invalid-three",3}, {"tz-short",3}, {"tz-invalid-four",3},
 {"parser-gmt",2}, {"parser-utc",2}, {"parser-other-three-zone",2},
 {"parser-four-zone",2}, {"parser-invalid-zone",2}
};
static uint64_t now(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return (uint64_t)t.tv_sec * 1000000000u + t.tv_nsec; }
static void init(void) {
 size_t w,i,j;
 for(w=0; w<sizeof(work)/sizeof(work[0]); ++w) for(i=0;i<N;++i) {
  struct item *p=&work[w].data[i]; unsigned m=rnd()%12,d=rnd()%7;
  if(w==0||w==5) strcpy(p->s,months[m]);
  if(w==1||w==6) strcpy(p->s,days[d]);
  if(w==2) strcpy(p->s,full[d]);
  if(w==5||w==6) p->s[2]='x';
  if(w==3||w==4) { for(j=0;j<3;++j) p->s[j]=1+rnd()%127; p->s[3]=0;
   if(base_checkday(p->s,3)>=0||base_checkmonth(p->s,3)>=0) p->s[2]='x'; }
  if(w==7||w==8) { j=rnd()%3; memset(p->s,'x',j); p->s[j]=0; }
  if(w>=9&&w<=11) { do { j=rnd()%(sizeof(corpus)/sizeof(corpus[0])); }
   while((w==10&&base_curl_getdate(corpus[j],NULL)==(time_t)-1)||(w==11&&base_curl_getdate(corpus[j],NULL)!=(time_t)-1)); strcpy(p->s,corpus[j]); }
  if(w==12) snprintf(p->s,sizeof(p->s),"%s, 06 %s 1994 08:49:37 GMT",days[d],months[m]);
  if(w==13) snprintf(p->s,sizeof(p->s),"%s, 06-%s-94 08:49:37 GMT",full[d],months[m]);
  if(w==14) snprintf(p->s,sizeof(p->s),"%s %s  6 08:49:37 1994",days[d],months[m]);
  if(w==15) strcpy(p->s,"20040912 15:05:58 -0700");
  if(w==16) { strcpy(p->s,months[m]); p->s[0]='x'; }
  if(w==17) { strcpy(p->s,days[d]); p->s[0]='x'; }
  if(w==18) strcpy(p->s,"GMT");
  if(w==19) strcpy(p->s,"UTC");
  if(w==20) strcpy(p->s,zones3[rnd()%(sizeof(zones3)/sizeof(zones3[0]))]);
  if(w==21) strcpy(p->s,zones4[rnd()%(sizeof(zones4)/sizeof(zones4[0]))]);
  if(w==22) { static const char *bad[]={"GNT","GMS","GmT","UTX","XTC","ZZZ","gmT","UTc"};
   strcpy(p->s,bad[rnd()%(sizeof(bad)/sizeof(bad[0]))]);p->s[3]=0; }
  if(w==23) { static const char *shortzones[]={"A","Z","J","UT","NT","GT","uT","j","Y"};
   strcpy(p->s,shortzones[rnd()%(sizeof(shortzones)/sizeof(shortzones[0]))]); }
  if(w==24) { static const char *bad[]={"GMTX","UTCX","CESt","ZZZZ","GMTA","UTCA"};
   strcpy(p->s,bad[rnd()%(sizeof(bad)/sizeof(bad[0]))]); }
  if(w==25||w==26) snprintf(p->s,sizeof(p->s),"%s, 06 %s 1994 08:49:37 %s",days[d],months[m],w==25?"GMT":"UTC");
  if(w==27) snprintf(p->s,sizeof(p->s),"%s, 06 %s 1994 08:49:37 %s",days[d],months[m],zones3[rnd()%(sizeof(zones3)/sizeof(zones3[0]))]);
  if(w==28) snprintf(p->s,sizeof(p->s),"%s, 06 %s 1994 08:49:37 %s",days[d],months[m],zones4[rnd()%(sizeof(zones4)/sizeof(zones4[0]))]);
  if(w==29) { static const char *bad[]={"GMTX","UTCX","gmT","UTc","GNT","UTX"};
   snprintf(p->s,sizeof(p->s),"%s, 06 %s 1994 08:49:37 %s",days[d],months[m],bad[rnd()%(sizeof(bad)/sizeof(bad[0]))]); }
  if(w<=2) for(j=0;p->s[j];++j) if(rnd()&1) p->s[j] ^= 0x20;
  p->len=strlen(p->s);
 }
}
static double measure(struct workload *w,int packed) {
 unsigned r,i; uint64_t sum=0,start=now();
 if(w->kind==2) { time_t (*fn)(const char *,const time_t *)=packed?pack_curl_getdate:base_curl_getdate;
  for(r=0;r<REPS;++r) for(i=0;i<N;++i) sum+=(uint64_t)fn(w->data[i].s,NULL); }
 else { int (*fn)(const char *,size_t)=w->kind==3?(packed?pack_unit_checktz:base_unit_checktz):w->kind?(packed?pack_checkday:base_checkday):(packed?pack_checkmonth:base_checkmonth);
  for(r=0;r<REPS;++r) for(i=0;i<N;++i) sum+=(uint64_t)fn(w->data[i].s,w->data[i].len); }
 { uint64_t end=now(); sink=sum; return (double)(end-start)/(REPS*N); }
}
static void check_workloads(void) {
 size_t w,i;
 for(w=0;w<sizeof(work)/sizeof(work[0]);++w) for(i=0;i<N;++i) {
  struct item *p=&work[w].data[i];
  if(w==18||w==19) assert(base_unit_checktz(p->s,p->len)==0);
  if(w==20||w==21) assert(base_unit_checktz(p->s,p->len)!=-1);
  if(w==22||w==24) assert(base_unit_checktz(p->s,p->len)==-1);
  if(w>=25&&w<=28) assert(base_curl_getdate(p->s,NULL)!=(time_t)-1);
  if(w==29) assert(base_curl_getdate(p->s,NULL)==(time_t)-1);
  if(work[w].kind==2) assert(base_curl_getdate(p->s,NULL)==pack_curl_getdate(p->s,NULL));
  else if(work[w].kind==3) assert(base_unit_checktz(p->s,p->len)==pack_unit_checktz(p->s,p->len));
  else if(work[w].kind==1) assert(base_checkday(p->s,p->len)==pack_checkday(p->s,p->len));
  else assert(base_checkmonth(p->s,p->len)==pack_checkmonth(p->s,p->len));
 }
}
static void verify(void) {
 unsigned a,b,c,i,j; char s[128]; uint64_t count=0;
 /* Every byte triplet, including NUL and high-bit bytes; exactly 3 bytes allocated. */
 char *p=malloc(3); assert(p);
 for(a=0;a<256;++a) for(b=0;b<256;++b) for(c=0;c<256;++c) {
  p[0]=(char)a;p[1]=(char)b;p[2]=(char)c;
  assert(base_checkday(p,3)==pack_checkday(p,3));
  assert(base_checkmonth(p,3)==pack_checkmonth(p,3)); ++count;
 }
 free(p);
 /* checktz's production callers supply ASCII names; avoid its preexisting
    signed-shift behavior for non-ASCII bytes. Check all ASCII triplets. */
 p=malloc(3);assert(p);
 for(a=0;a<128;++a) for(b=0;b<128;++b) for(c=0;c<128;++c) {
  p[0]=(char)a;p[1]=(char)b;p[2]=(char)c;
  assert(base_unit_checktz(p,3)==pack_unit_checktz(p,3));
 }
 free(p);
 p=malloc(4);assert(p);
 for(a='A';a<='Z';++a) for(b='A';b<='Z';++b) for(c='A';c<='Z';++c) for(i='A';i<='Z';++i) {
  p[0]=(char)a;p[1]=(char)b;p[2]=(char)c;p[3]=(char)i;
  assert(base_unit_checktz(p,4)==pack_unit_checktz(p,4));
 }
 free(p);
 for(i=0;i<3;++i) { p=malloc(i?i:1); memset(p,'M',i?i:1);
  assert(pack_checkday(p,i)==-1); assert(pack_checkmonth(p,i)==-1); free(p); }
 for(i=0;i<7;++i) for(j=0;j<512;++j) {
  size_t k,n=strlen(full[i]); strcpy(s,full[i]);
  for(k=0;k<n;++k) if(j&(1u<<k)) s[k]^=0x20;
  for(k=0;k<=n;++k) assert(base_checkday(s,k)==pack_checkday(s,k));
  s[3]='x'; assert(pack_checkday(s,n)==-1);
 }
 for(i=0;i<sizeof(corpus)/sizeof(corpus[0]);++i) assert(base_curl_getdate(corpus[i],NULL)==pack_curl_getdate(corpus[i],NULL));
 for(i=0;i<100000;++i) { size_t n=rnd()%127; for(j=0;j<n;++j) s[j]=(char)(1+rnd()%127);s[n]=0;
  assert(base_curl_getdate(s,NULL)==pack_curl_getdate(s,NULL)); }
 state=0x20261015;init();check_workloads();
 printf("Timezone checks: 2097152 ASCII triplets, 456976 uppercase four-letter names, and all 30 benchmark datasets matched\n");
 printf("PASS: %llu byte triplets, exact-size/short buffers, full weekday case variants and lengths, %zu corpus dates, 100000 random ASCII parser inputs\n",(unsigned long long)count,sizeof(corpus)/sizeof(corpus[0]));
}
int main(int argc,char **argv) {
 unsigned round,i,j,order[sizeof(work)/sizeof(work[0])];
 (void)argv;
 if(argc>1) { verify();return 0; }
 init();check_workloads();
 for(i=0;i<sizeof(work)/sizeof(work[0]);++i) { measure(&work[i],0);measure(&work[i],1); }
 puts("round,workload,first,base_ns,packed_ns");
 for(round=0;round<ROUNDS;++round) {
  for(i=0;i<sizeof(work)/sizeof(work[0]);++i) order[i]=i;
  for(i=sizeof(work)/sizeof(work[0])-1;i>0;--i) { unsigned t; j=rnd()%(i+1);t=order[i];order[i]=order[j];order[j]=t; }
  for(i=0;i<sizeof(work)/sizeof(work[0]);++i) { int first=rnd()&1; double t[2];
   t[first]=measure(&work[order[i]],first);t[!first]=measure(&work[order[i]],!first);
   printf("%u,%s,%d,%.6f,%.6f\n",round,work[order[i]].name,first,t[0],t[1]); }
 }
 return 0;
}
