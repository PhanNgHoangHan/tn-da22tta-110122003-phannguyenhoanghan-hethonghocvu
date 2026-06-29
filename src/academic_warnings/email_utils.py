from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.db import IntegrityError
from students.models import HocKy, Lop
from academic_warnings.models import CanhBaoHocVu, LichSuGuiEmailBaoCao

def check_and_send_semester_reports(today):
    """
    Check if the current date is the start date of the active semester.
    If so, trigger automatic email reports for the previous semester:
    - Semester 1 report is sent on the start date of Semester 2.
    - Semester 2 report is sent on the start date of Semester 1 of the next year.
    """
    active_hk = HocKy.objects.filter(la_hien_tai=True).first()
    if not active_hk or not active_hk.ngay_bat_dau:
        return

    # Check if today is the start date of the active semester
    if active_hk.ngay_bat_dau != today:
        return

    # Determine report semester
    report_hk = None
    if active_hk.ky == '2':
        # Today starts HK2 -> Send report for HK1 of the same school year
        report_hk = HocKy.objects.filter(nam_hoc=active_hk.nam_hoc, ky='1').first()
    elif active_hk.ky == '1':
        # Today starts HK1 -> Send report for HK2 of the previous school year
        try:
            years = active_hk.nam_hoc.split('-')
            if len(years) == 2:
                prev_start_year = int(years[0].strip()) - 1
                prev_end_year = prev_start_year + 1
                prev_nam_hoc = f"{prev_start_year}-{prev_end_year}"
                report_hk = HocKy.objects.filter(nam_hoc=prev_nam_hoc, ky='2').first()
        except Exception:
            pass

    if not report_hk:
        return

    print(f"[Email Reports] Starting auto email reports for semester: {report_hk}")

    # Fetch all classes with advisors
    classes = Lop.objects.select_related('covan').all()
    for lop in classes:
        if not lop.covan or not lop.covan.email:
            continue

        # Check if already sent to prevent duplicate emails
        if LichSuGuiEmailBaoCao.objects.filter(lop=lop, hoc_ky=report_hk).exists():
            continue

        # Fetch warnings of this class in the report semester
        warnings = CanhBaoHocVu.objects.filter(
            sinh_vien__lop=lop,
            hoc_ky=report_hk
        ).select_related('sinh_vien')

        total_students = lop.sinh_viens.count()
        warned_count = warnings.filter(muc_canh_bao='canh_bao').count()
        withdraw_count = warnings.filter(muc_canh_bao='buoc_thoi_hoc').count()

        # Render HTML email
        context = {
            'hoc_ky': f"Học kỳ {report_hk.ky} - Năm học {report_hk.nam_hoc}",
            'lop': lop,
            'covan_name': lop.covan.full_name or lop.covan.username,
            'total_students': total_students,
            'warned_count': warned_count,
            'withdraw_count': withdraw_count,
            'warnings': warnings,
        }
        html_content = render_to_string('emails/bao_cao_canh_bao.html', context)
        
        # Email settings
        subject = f"[TVU] Báo cáo Cảnh báo Học vụ - HK{report_hk.ky} ({report_hk.nam_hoc}) - Lớp {lop.ten_lop}"
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'giaovu@tvu.edu.vn')
        to_email = lop.covan.email

        # Plain text summary fallback
        text_content = (
            f"Kính gửi Thầy/Cô {lop.covan.full_name or lop.covan.username},\n\n"
            f"Dưới đây là tóm tắt kết quả cảnh báo học vụ lớp {lop.ten_lop} học kỳ HK{report_hk.ky} - {report_hk.nam_hoc}:\n"
            f"- Tổng số sinh viên: {total_students}\n"
            f"- Số sinh viên bị cảnh báo học vụ: {warned_count}\n"
            f"- Số sinh viên buộc thôi học: {withdraw_count}\n\n"
            f"Vui lòng truy cập http://127.0.0.1:8000/ để xem chi tiết."
        )

        try:
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
            msg.attach_alternative(html_content, "text/html")
            msg.send(fail_silently=True)

            # Record in history
            LichSuGuiEmailBaoCao.objects.create(lop=lop, hoc_ky=report_hk)
            print(f"[Email Reports] Successfully sent report for class {lop.ten_lop} to {to_email}")
        except IntegrityError:
            # Handle race conditions in case another thread created it
            pass
        except Exception as e:
            print(f"[Email Reports] Error sending email for class {lop.ten_lop}: {e}")
