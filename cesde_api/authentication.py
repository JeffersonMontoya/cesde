from rest_framework.decorators import authentication_classes, permission_classes
from datetime import timedelta
from django.utils import timezone
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import LoginAttempt
from .serializer import UserSerializer


@api_view(["POST"])
def login(request):
    # Intentar obtener el usuario por el nombre de usuario
    try:
        user = User.objects.get(username=request.data.get('username'))
    except User.DoesNotExist:
        # Si el usuario no existe, retornar un mensaje de error
        return Response({"error": "Usuario no existente"}, status=status.HTTP_404_NOT_FOUND)

    # Obtener o crear un registro de intento de inicio de sesión para el usuario
    login_attempt, created = LoginAttempt.objects.get_or_create(user=user)

    # Verificar si el usuario ha alcanzado el límite de intentos fallidos
    if login_attempt.attempts == 3:
        # Calcular el tiempo transcurrido desde el último intento fallido
        time_since_last_attempt = timezone.now() - login_attempt.last_attempt
        if time_since_last_attempt < timedelta(minutes = 1):
            # Si han pasado menos de 10 minutos, bloquear el acceso
            return Response({"error": "Usuario bloqueado. Por favor, intente de nuevo más tarde (5 minutos)."}, status=status.HTTP_403_FORBIDDEN)

    #si se hacen mas de 5 intentos fallidos se bloquea el usuario
    if login_attempt.attempts >5:
        login_attempt.permanently_blocked=True
        login_attempt.save()

    # Verificar si el usuario está bloqueado permanentemente
    if login_attempt.permanently_blocked:
        return Response({"error": "Usuario bloqueado permanentemente, contacte al administrador."}, status=status.HTTP_403_FORBIDDEN)

    # Verificar si la contraseña es correcta
    if not user.check_password(request.data.get('password')):
        # Incrementar el contador de intentos fallidos si la contraseña es incorrecta
        login_attempt.increment_attempts()
        return Response({"error": "Contraseña incorrecta"}, status=status.HTTP_400_BAD_REQUEST)

    # Si la contraseña es correcta, reiniciar los intentos fallidos
    login_attempt.reset_attempts()

    # Obtener o crear un token para el usuario
    token, created = Token.objects.get_or_create(user=user)

    # Retornar la respuesta con el token y los datos del usuario
    return Response({
        "token": token.key,
        "user": {
            "username": user.username,
            "email": user.email,
            # Añadir otros campos que quieras devolver
        }
    }, status=status.HTTP_200_OK)


@api_view(["POST"])
def register(request):
    serializer = UserSerializer(data=request.data)

    if serializer.is_valid():
        # Guardar el usuario y obtener la instancia
        user = serializer.save()

        # Crear el token para el usuario
        token, created = Token.objects.get_or_create(user=user)

        # Retornar la respuesta con el token y los datos del usuario
        return Response({
            "token": token.key,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
                # No incluyas la contraseña por seguridad
            }
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def profile(request):
    # Imprimir el ID del usuario autenticado
    print(request.user.id)

    # Serializar el usuario autenticado
    serializer = UserSerializer(instance=request.user)

    # Devolver la respuesta con los datos del usuario y un estado HTTP 200 OK
    return Response(serializer.data, status=status.HTTP_200_OK)