from datetime import date
from django.utils import timezone
from django.db import IntegrityError
from students.models import HocKy

class SemesterAutoCreateMiddleware:
    last_checked_date = None

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        today = timezone.localtime(timezone.now()).date()
        if SemesterAutoCreateMiddleware.last_checked_date != today:
            self.check_and_create_semester(today)
            SemesterAutoCreateMiddleware.last_checked_date = today

        response = self.get_response(request)
        return response

    def check_and_create_semester(self, today):
        ky = None
        nam_hoc = None
        ngay_bat_dau = None
        ngay_ket_thuc = None

        # Semester 1: October to January next year
        if today.month in [10, 11, 12, 1]:
            ky = '1'
            if today.month >= 10:
                start_year = today.year
                end_year = today.year + 1
            else:
                start_year = today.year - 1
                end_year = today.year
            nam_hoc = f"{start_year}-{end_year}"
            ngay_bat_dau = date(start_year, 10, 1)
            ngay_ket_thuc = date(end_year, 1, 31)

        # Semester 2: February to June
        elif today.month in [2, 3, 4, 5, 6]:
            ky = '2'
            start_year = today.year - 1
            end_year = today.year
            nam_hoc = f"{start_year}-{end_year}"
            ngay_bat_dau = date(end_year, 2, 1)
            ngay_ket_thuc = date(end_year, 6, 30)

        if ky and nam_hoc:
            try:
                hk, created = HocKy.objects.get_or_create(
                    ky=ky,
                    nam_hoc=nam_hoc,
                    defaults={
                        'ngay_bat_dau': ngay_bat_dau,
                        'ngay_ket_thuc': ngay_ket_thuc,
                        'la_hien_tai': True
                    }
                )
                if not created and not hk.la_hien_tai:
                    hk.la_hien_tai = True
                    hk.save()
            except IntegrityError:
                pass
            except Exception:
                pass

        # Trigger automatic emailing of class warning reports
        try:
            from academic_warnings.email_utils import check_and_send_semester_reports
            check_and_send_semester_reports(today)
        except Exception:
            pass

