from models.models import Complaint ,db
from datetime import datetime, timezone


class ComplaintService:
    # this for get all complaints   
    @staticmethod
    def get_all_complaints():
        return(
            Complaint.query.orderby(Complaint.created_at.desc()).all()
        )
    


    # This for get complaint by id
    @staticmethod
    def get_complaint_by_id(complaint_id):
        return Complaint.query.get(complaint_id)
    
    # This for get all unresolved complaints
    @staticmethod
    def get_unresolved_complaints(): 
        complaints = Complaint.query.filter_by(
        is_resolved=False
         ).order_by(
        Complaint.created_at.desc()
        ).all()

        return complaints, "تم العثور على الشكاوى"
  
    # this for display the complaint details
    @staticmethod
    def get_complaint_details(complaint_id):
        complaint = Complaint.query.get(complaint_id)
        if not complaint:
            return None , "الشكوى غير موجودة"
        
        return complaint , "تم العثور على الشكوى بنجاح"

    # This for create new complaint for agent
    @staticmethod
    def create_complaint(message,phone_number):
        new_complaint = Complaint(
            phone_number=phone_number,
            complaint_text=message
        )
        db.session.add(new_complaint)
        db.session.commit()
        return Complaint.id
    
    from models.models import db, Complaint


    def save_complaint(phone: str, complaint: str) -> str:
       """Save complaint to DB and return confirmation message."""
       record = Complaint(
        phone_number=phone,
        complaint_text=complaint,
        is_resolved=False,
        created_at=datetime.now(timezone.utc)
      )
       db.session.add(record)
       db.session.commit()

       return "تم تسجيل شكواك بنجاح ✅\nسيتم التواصل معك في أقرب وقت."
 

    # this for resolve complaint by id
    @staticmethod
    def resolve_complaint(complaint_id):
        complaint = Complaint.query.get(complaint_id)
        if not complaint:
            return False , "الشكوى غير موجودة"
        
        complaint.is_resolved = True
        complaint.resolved_at = datetime.now(timezone.utc)
        db.session.commit()
        return True , "تم حل الشكوى بنجاح"
    

    # this for update complaint status by id  
    @staticmethod
    def update_complaint_status(complaint_id, is_resolved):
        complaint = Complaint.query.get(complaint_id)

        if not complaint:
            return False, "الشكوى غير موجودة"

        complaint.is_resolved = is_resolved

        if is_resolved:
            complaint.resolved_at = datetime.now(timezone.utc)
        else:
            complaint.resolved_at = None

        db.session.commit()

        return True, "تم تحديث حالة الشكوى"
