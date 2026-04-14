const DEFAULT_RSA_N = 3233n;
const DEFAULT_RSA_E = 17n;
const DEFAULT_RSA_D = 2753n;

export function modPow(base, exponent, modulus) {
  if (modulus === 1n) {
    return 0n;
  }

  let result = 1n;
  let b = base % modulus;
  let e = exponent;

  while (e > 0n) {
    if (e % 2n === 1n) {
      result = (result * b) % modulus;
    }
    e = e / 2n;
    b = (b * b) % modulus;
  }

  return result;
}

export function rsaEncryptText(
  plainText,
  n = DEFAULT_RSA_N,
  e = DEFAULT_RSA_E,
) {
  return Array.from(plainText).map((ch) => {
    const m = BigInt(ch.codePointAt(0));
    return Number(modPow(m, e, n));
  });
}

export function rsaDecryptText(
  encryptedValues,
  n = DEFAULT_RSA_N,
  d = DEFAULT_RSA_D,
) {
  return encryptedValues
    .map((value) => {
      if (!Number.isInteger(value)) {
        throw new Error("encrypted_payload must contain integers");
      }
      const decryptedCode = Number(modPow(BigInt(value), d, n));
      return String.fromCodePoint(decryptedCode);
    })
    .join("");
}

export function rsaEncryptJson(payload, n = DEFAULT_RSA_N, e = DEFAULT_RSA_E) {
  const plainText = JSON.stringify(payload);
  return rsaEncryptText(plainText, n, e);
}

export const RSA_DEMO_PUBLIC_KEY = { n: DEFAULT_RSA_N, e: DEFAULT_RSA_E };
export const RSA_DEMO_PRIVATE_KEY = { n: DEFAULT_RSA_N, d: DEFAULT_RSA_D };
