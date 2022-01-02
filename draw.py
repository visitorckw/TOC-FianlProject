import cv2
import numpy as np
class draw:
    def __init__(self):
        self.black = []
        self.white = []
        self.space = 16
        self.margin = 20
        self.IMG_SIZE = (256,256)
    def trans(self, str1, str2):
        x = ord(str1) - ord('A')
        y = ord(str2) - ord('A')
        return [self.margin + x * self.space, self.margin + y * self.space]
    def draw(self, filename):
        img = np.zeros((self.IMG_SIZE[0], self.IMG_SIZE[1], 3), np.uint8)
        # img.fill(200)
        for x in range(self.IMG_SIZE[0]):
            for y in range(self.IMG_SIZE[1]):
                img[x][y][0] = 19
                img[x][y][1] = 69
                img[x][y][2] = 139
        for i in range(15):
            text = chr(ord('A') + i)
            cv2.putText(img, text, (0, self.margin + self.space * i), cv2.FONT_HERSHEY_DUPLEX,0.3, (0, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(img, text, (self.margin + self.space * i, self.margin //2 ), cv2.FONT_HERSHEY_DUPLEX,0.3, (0, 255, 255), 1, cv2.LINE_AA)
        for i in range(15):
            cv2.line(img, (self.margin + self.space*i, self.margin), (self.margin+self.space*i, self.margin + 14 * self.space), (255,255,255), 1)
            cv2.line(img, (self.margin, self.margin+self.space*i), (self.margin + 14 * self.space, self.margin+self.space*i), (255,255,255), 1)
        for p in self.black:
            cv2.circle(img,(p[0], p[1]), self.space//2, (0, 0, 0), -1)
        for p in self.white:
            cv2.circle(img,(p[0], p[1]), self.space//2, (255, 255, 255), -1)
        cv2.imwrite(filename, img)
        return 0
pic = draw()
pic.draw('demp.png')