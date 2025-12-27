export interface ProductInfo { name?: string; ingredientsText?: string }
export interface ProductLookupProvider { lookup(barcode: string): Promise<ProductInfo | null> }

export class OpenFoodFactsProvider implements ProductLookupProvider {
  async lookup(barcode: string): Promise<ProductInfo | null> {
    try {
      const url = `https://world.openfoodfacts.org/api/v0/product/${barcode}.json`
      const res = await fetch(url)
      if (!res.ok) return null
      const data = await res.json()
      const status = data?.status
      if (status !== 1) return null
      const product = data?.product
      return {
        name: product?.product_name || product?.brands,
        ingredientsText: product?.ingredients_text || product?.ingredients_text_en || null
      }
    } catch {
      return null
    }
  }
}

export class MockProvider implements ProductLookupProvider {
  async lookup(barcode: string): Promise<ProductInfo | null> {
    if (barcode === '5901234123457') return { name: 'Sample Sauce', ingredientsText: 'Water, salt, milk powder' }
    return null
  }
}

export function getProvider(): ProductLookupProvider {
  const useMock = process.env.USE_MOCK_PROVIDER === 'true'
  return useMock ? new MockProvider() : new OpenFoodFactsProvider()
}
