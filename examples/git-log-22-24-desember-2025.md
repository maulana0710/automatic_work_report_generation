commit b0551296a70187e010cd633659166d027dbb80b8
Merge: a8eebbc 75fbed5
Author: vicky maulana <vickymaulana0710@gmail.com>
Date:   Wed Dec 24 01:28:45 2025 +0000

    Merge branch 'feat/purchase-brt-features' into 'master'
    
    update environment config, warehouse keys, and payment confirmation
    
    See merge request mobile-app-development/wansis_store!15

commit 75fbed534a7b7b93b5963436a793e495ad74d4c4
Author: vicky maulana <vickymaulana0710@gmail.com>
Date:   Wed Dec 24 08:24:44 2025 +0700

    update env for staging and development

commit 3a40fcd2b183d1d0dd087f7226bcf88b04644dde
Author: vicky maulana <vickymaulana0710@gmail.com>
Date:   Tue Dec 23 17:36:54 2025 +0700

    adding get response after create warehouse and put the "key" to "warehouse" for a payload create order

commit 03516de761e5698b1d4d28c67e7554c6317e49c9
Author: vicky maulana <vickymaulana0710@gmail.com>
Date:   Tue Dec 23 14:29:50 2025 +0700

    adding multiple payment confirmation

commit 66e6f611eea6c7e003110b7015639124deb07d43
Author: vicky maulana <vickymaulana0710@gmail.com>
Date:   Tue Dec 23 13:46:53 2025 +0700

    fixing snackbar to shown at the root overlay, so if there is any dialog or sheet the snackbar will not being hidded

commit 3154ea906e6d610e11ed4d558da0fe59c171cc3a
Author: vicky maulana <vickymaulana0710@gmail.com>
Date:   Tue Dec 23 10:42:44 2025 +0700

    fixing at order detail sheet to showing "Daftar Barang" and changing conditional at create purchase brt to update_bonus=false and not got bonus item yet then don't grouping

commit 809458be4c2e393c040ef479f4722873b7ef7b7f
Merge: 217d179 a8eebbc
Author: vicky maulana <vickymaulana0710@gmail.com>
Date:   Tue Dec 23 09:31:35 2025 +0700

    Merge branch 'master' of http://gitlab.local/mobile-app-development/wansis_store into feat/purchase-brt-features

commit a8eebbca2d311ba4e4eb5f093c4ade89bb9d3b0d
Merge: 4d27299 8bf7134
Author: vicky maulana <vickymaulana0710@gmail.com>
Date:   Tue Dec 23 02:28:12 2025 +0000

    Merge branch 'fix/create-purchase-brt' into 'master'
    
    change conditional for "update_bonus" is false then don't grouping and can't...
    
    See merge request mobile-app-development/wansis_store!14

commit 217d17937fc55870ab25726f80853e4a143e9265
Author: vicky maulana <vickymaulana0710@gmail.com>
Date:   Tue Dec 23 09:24:37 2025 +0700

    removing sheet if user tap on "Pesan" navigation and make redirect to "purchase_brt" route, adding feature for uploading proof of payment or tempo if user has a "purchase_payment_type": "4", adding conditional if orders has a "pay" value not 0 then hide the feature to upload proof of payment and change all price to using format currency helper

commit 8bf713487b46821bacedd5efd89c8c92e8936c8b
Author: vicky maulana <vickymaulana0710@gmail.com>
Date:   Mon Dec 22 18:00:59 2025 +0700

    change conditional for "update_bonus" is false then don't grouping and can't be grouping with another item

commit 4d2729900654d1b2d54adcc58c97223b5f1b347e
Merge: 7f91f58 2071628
Author: vicky maulana <vickymaulana0710@gmail.com>
Date:   Mon Dec 22 10:49:12 2025 +0000

    Merge branch 'fix/create-purchase-brt' into 'master'
    
    Update: Item Bonus Handling, Field Auto-Submit, and Order Detail Enhancements
    
    See merge request mobile-app-development/wansis_store!13

commit 207162868870d044f80b3ba50e171334f712134a
Author: vicky maulana <vickymaulana0710@gmail.com>
Date:   Mon Dec 22 17:32:24 2025 +0700

    add handling for bonus item with different perent but same "kategori" then pick from first parent then pick the second perent bonus

commit 4fbf010819f3083a7673e9414edb836d63be3428
Author: vicky maulana <vickymaulana0710@gmail.com>
Date:   Mon Dec 22 17:15:30 2025 +0700

    updating on item bonus if perent item at key "update_bonus" is false then show item bonus child and cant pick item bonus or change mode from bonus to special price

commit 3564a807a98792386e6546a7fe4b59b1a538e61f
Author: vicky maulana <vickymaulana0710@gmail.com>
Date:   Mon Dec 22 14:28:07 2025 +0700

    adding regex to validate phone number
