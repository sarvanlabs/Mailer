SELECT count(*)
        from company_master_new cmn where
        cmn.Class_of_Company = 'Private' 
        and cmn.Whether_Listed_or_not = 'Unlisted'
        and cmn.Paid_up_Capital_Rs < 2000000
        and cmn.is_unsubscribed = 0
        and cmn.Email_Id IS NOT NULL
        and cmn.Email_Id != ''
        and cmn.Date_of_Incorporation >= '2025-11-01' AND cmn.Date_of_Incorporation < '2025-11-30'
        and cmn.Company_Name not like '%technology%'
        
        SELECT cmn.Company_Name, 
        cmn.Email_Id, 
        cmn.is_unsubscribed
        from company_master_new cmn where
        cmn.Class_of_Company = 'Private' 
        and cmn.Whether_Listed_or_not = 'Unlisted'
        and cmn.Paid_up_Capital_Rs < 2000000
        and cmn.is_unsubscribed = 0
        and cmn.Email_Id IS NOT NULL
        and cmn.Email_Id != ''
        and cmn.Date_of_Incorporation >= '2025-08-01' AND cmn.Date_of_Incorporation < '2025-08-31'
        and cmn.Company_Name not like '%technology%'
        
        
        select * from company_master_new cmn where cmn.Email_Id='vamsi@lpgroup.co.in'


        mysql --version
mysql  Ver 8.4.6 for Linux on x86_64 (MySQL Community Server - GPL)