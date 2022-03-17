# NCP2 package reverse engineering
Let's pack/unpack NCP2 package!

## 왜 하나?
리버스엔지니어링은 아주 재미없는 작업이지만, ncp2 패키지에 있는 mp3가 필요하여 작업하게 되었다.
패키지 파일을 열고 계산기 두들기다 보니 어느센가 간단한 명세서까지 작성할 수 있었다.
이왕 시작한 김에 unpacker까지 설계해보자!

## 어떤 걸로 작성할까?
C언어로 개발하면 더 재밌고 머리아프겠지만, 파이썬도 손에 더 익힐 겸 파이썬으로 개발할 계획이다.

## 지금까지의 작업
### v2022.3.17.0
샘플로 ncp2파일 하나를 지정하여 분석한 (러프한)명세서.
FTBL 명령의 경우 내부 file list 구조에 대한 명세가 필요하다. (이미 분석은 완료했지만 문서 구조가 잡히면 정리)

각 바이트 구간별로 설명을 적어놨으나 뇌피셜이다.
```
# 1~4 (4)
# NPQF (If 'RIFF' then 'RIFFNPQF' and add 4 more bytes each bytes of below list.)

# 5~12 (8) Unknown
# 01002004 03000300

# 13~24 (12) Unknown string
# ARESNPQ_Test

# 25~32 Zero padding
# 00000000 00000000

# 33~40 command start
# 50536110 64000000 : PSa(0x01)D

# 41~44 command
# INFO

# 45~48 size of command (byte)
# 2C000000 = 44
########################## 49~92 data block of command
# 49~52 Unknown
# 01000000

# 53~56 count of list
# 26000000

# 57~92 unknown
# 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000
########################## end

# 89~92 zero padding
# 00000000

# 93~96 command end
# 00005045 : PE

# 97~104 command start
# 50536110 64000000 : PSa(0x01)D

# 105~108 command
# FTBL

# 109~112 size of command (byte)
# 80090000 = 2432
########################## 113~2544 data block of command 
[64 bytes loop]
~108  file name
~4  file size
~4 00000000 : zero padding
~4 file length
~4 file_length repeat
~4 zero padding
[continue...]
########################## end

# 2545~2548 command end
# 00005045 : PE

# 2549~2556 command start
# 50536110 64000000 : PSa(0x01)D

# 2557~2560 command
# DATA

# 2561~2564 size of command (byte)
# 9C092E00 = 3017116
########################## 2564~3019680 data block of command
########################## end
# 3019681~3019684 command end
# 00005045 : PE

```

