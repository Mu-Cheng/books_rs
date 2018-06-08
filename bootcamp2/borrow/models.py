from django.db import models

STR_NUM = 18

# Create your models here.
class Borrow(models.Model):
    userid = models.IntegerField(verbose_name='用户id')
    book_link = models.TextField(max_length=255,verbose_name='图书链接')
    img_link = models.TextField(max_length=255,verbose_name='图片链接')
    book_name = models.TextField(max_length=255,verbose_name='图书名字')
    class Meta:
        verbose_name = '借阅管理'
        verbose_name_plural = verbose_name
    @staticmethod
    def get_borrowed(userid):
        borrowed = Borrow.objects.filter(userid=userid)
        return borrowed

    @staticmethod
    def get_borrowed_sum(userid):
        # print(userid)
        borrow_sum = Borrow.objects.filter(userid=userid).count()
        # print(borrow_sum)
        return borrow_sum

    def get_img_link(self):
        return 'http://118.89.162.148/img/{}'.format(self.img_link)
        # return 'http://img-1252422469.file.myqcloud.com/bookimg/'+self.img_link

    def get_first_p(self):
        tem = self.book_name
        if len(tem) > STR_NUM:
            return tem[:STR_NUM]
        else:
            return tem
    def get_book_id(self):
        return self.book_link.split('/')[-1]

    def get_content_has_second(self):
        return len(self.book_name) > STR_NUM

    def get_second_p(self):
        tem = self.book_name
        if len(tem) > STR_NUM:
            return tem[STR_NUM:]
        else:
            return ' '
