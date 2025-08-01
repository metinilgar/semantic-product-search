"""
Prompt sabitleri ve şablonları
Bu dosya uygulamada kullanılan tüm prompt'ları içerir.
"""

# LLM Analiz Prompt'u - Kullanıcı sorgularını analiz etmek için
QUERY_ANALYSIS_PROMPT = """
Aşağıdaki ürün arama sorgusunu analiz et ve yapılandırılmış bilgileri çıkar.

Input: "{query}"

Talimatlar:
- Sen, e-ticaret aramalarını analiz eden uzman bir yapay zekasın.
- Kullanıcı niyetini tespit et: ürün türleri, bağlamsal etiketler ve cinsiyet tercihini ('erkek'|'kadın' veya `null`) belirle.
- En alakalı 3–5 ürün türünü sırayla listele. İlk ürün türü, her zaman sorguda belirtilen ana ürün olmalıdır. Ürün türleri tek kelime olsun (ör. ceket, gömlek, ayakkabı).
- Renk, malzeme (ör: pamuk, deri), stil (ör: V yaka, dar paça) gibi tüm ürün niteliklerini tespit et.
- Genişletilmiş sorguyu (expanded_query) oluştururken, bunun bir ürün başlığı veya zengin bir ürün açıklaması gibi olmasını hedefle. Bu sorgu; tespit edilen cinsiyeti (eğer bağlamdan çıkarılabiliyorsa), ana ürün türünü, renk, malzeme gibi nitelikleri ve bağlamsal kelimeleri (ör: ofis, yazlık, spor, rahat) mutlaka içermelidir.
- “Hariç”, “dışında”, “olmayan” gibi negatif kısıtlamalar varsa, bunları ürün türleri listesinden ve genişletilmiş sorgudan tamamen çıkar; negatif kısıtlamayı özel bir alan olarak dönme.
- Cinsiyet sorguda açıkça belirtilmemişse **bağlam ve ürün türlerinden mantıksal olarak çıkar**. Eğer hiçbir bağlam sunmuyorsa `"gender": null` olarak ayarla.

Örnekler:
Query: "Ofis için siyah takım elbise lazım"  
→ gender: male  
→ product_types: ["takım_elbise","gömlek","ayakkabı","kravat"]  
→ expanded_query: "siyah resmi ofis takım elbise profesyonel iş giyim klasik kesim gömlek ve ayakkabı"

Query: "erkekler için günlük spor ayakkabı"  
→ gender: "male"  
→ product_types: ["ayakkabı","çorap","eşofman","şort"]  
→ expanded_query: "erkek günlük spor ayakkabı rahat konforlu yürüyüş ve koşu sneaker erkek spor çorap eşofman altı"

Query: "Dağ yürüyüşü için mont ve sırt çantası"  
→ gender: null  
→ product_types: ["mont","sırt_çantası","bot","yağmurluk"]  
→ expanded_query: "dağ yürüyüşü outdoor mont dayanıklı su geçirmez bot ve hafif sırt çantası"

Query: "Deri olmayan siyah kadın ceketi" 
→ gender: "female"
→ product_types: ["ceket", "mont", "trençkot", "gömlek"]
→ expanded_query: "siyah kadın ceket kumaş mevsimlik bomber kolej mont su geçirmez trençkot"


Şimdi aşağıdaki sorguyu analiz et: "{query}"
"""


def get_query_analysis_prompt(query: str) -> str:
    """
    Sorgu analizi için prompt'u formatla
    
    Args:
        query: Analiz edilecek kullanıcı sorgusu
        
    Returns:
        Formatlanmış prompt metni
    """
    return QUERY_ANALYSIS_PROMPT.format(query=query)