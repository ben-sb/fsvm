#include <stdio.h>

int main(int argc, char* argv[]) {
	puts("flag:");
	char flag[29];
	scanf("%s", flag);
	if ((((-flag[0]) + 111) + (((-flag[1]) + 112) + (((-flag[2]) + 101) + (((-flag[3]) + 110) + (((-flag[4]) + 69) + (((-flag[5]) + 67) + (((-flag[6]) + 83) + (((-flag[7]) + 67) + (((-flag[8]) + 123) + (((-flag[9]) + 115) + (((-flag[10]) + 117) + (((-flag[11]) + 112) + (((-flag[12]) + 101) + (((-flag[13]) + 114) + (((-flag[14]) + 101) + (((-flag[15]) + 97) + (((-flag[16]) + 115) + (((-flag[17]) + 121) + (((-flag[18]) + 118) + (((-flag[19]) + 109) + (((-flag[20]) + 99) + (((-flag[21]) + 52) + (((-flag[22]) + 101) + (((-flag[23]) + 56) + (((-flag[24]) + 55) + (((-flag[25]) + 99) + (((-flag[26]) + 52) + (((-flag[27]) + 100) + ((-flag[28]) + 125))))))))))))))))))))))))))))) != "00000000000000000000000000000") {
		puts("no");
		return 0;
	} else {
		puts("ok");
		return 0;
	}
}